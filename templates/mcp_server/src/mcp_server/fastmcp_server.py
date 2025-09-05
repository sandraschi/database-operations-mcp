"""
FastMCP 2.13 Server Implementation

This module provides a FastMCP 2.13 compliant server that handles stdio communication
and manages tool registration and execution.
"""
import sys
import json
import asyncio
import signal
from typing import Dict, Any, Optional, List, Callable, Awaitable, TypeVar, Union
from pathlib import Path
import logging

# Import FastMCP types
try:
    from mcp.types import Tool, ToolCall, ToolResult, ToolError, ToolDefinition
    from mcp.server import FastMCPServer, FastMCPTool
    from mcp.utils.logging import get_logger
except ImportError:
    # Fallback for development
    from typing import TypedDict, Any, Optional, Dict, List, TypeVar, Callable, Awaitable, Union
    
    class ToolCall(TypedDict):
        id: str
        name: str
        arguments: Dict[str, Any]
    
    class ToolResult(TypedDict):
        id: str
        result: Any
    
    class ToolError(TypedDict):
        id: str
        error: str
    
    class ToolDefinition(TypedDict):
        name: str
        description: str
        parameters: Dict[str, Any]
    
    class FastMCPTool:
        def __init__(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
            self.name = name
            self.description = description
            self.parameters = parameters
            self.func = func
        
        async def __call__(self, **kwargs) -> Any:
            return await self.func(**kwargs)
    
    class FastMCPServer:
        def __init__(self):
            self.tools: Dict[str, FastMCPTool] = {}
        
        def register_tool(self, tool: FastMCPTool) -> None:
            self.tools[tool.name] = tool
        
        def get_tool(self, name: str) -> Optional[FastMCPTool]:
            return self.tools.get(name)
        
        def get_tools(self) -> Dict[str, FastMCPTool]:
            return self.tools.copy()

logger = get_logger(__name__) if 'get_logger' in globals() else logging.getLogger(__name__)

# Type variables
T = TypeVar('T')
JsonRpcId = Union[str, int, float, None]
JsonRpcParams = Union[Dict[str, Any], List[Any], None]

class JsonRpcRequest(TypedDict, total=False):
    jsonrpc: str
    id: JsonRpcId
    method: str
    params: JsonRpcParams

class JsonRpcResponse(TypedDict, total=False):
    jsonrpc: str
    id: JsonRpcId
    result: Any
    error: Dict[str, Any]

class FastMCP13Server(FastMCPServer):
    """FastMCP 2.13 compliant server implementation."""
    
    def __init__(self, debug: bool = False):
        """Initialize the FastMCP server.
        
        Args:
            debug: Whether to enable debug logging.
        """
        super().__init__()
        self.debug = debug
        self.running = False
        self._request_handlers = {
            "initialize": self._handle_initialize,
            "tool/execute": self._handle_tool_execute,
            "tool/list": self._handle_tool_list,
            "tool/describe": self._handle_tool_describe,
            "shutdown": self._handle_shutdown,
        }
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
    
    async def start(self) -> None:
        """Start the server and begin processing messages from stdio."""
        if self.running:
            logger.warning("Server is already running")
            return
        
        self.running = True
        logger.info("Starting FastMCP 2.13 server...")
        
        try:
            # Set up stdio communication
            loop = asyncio.get_event_loop()
            
            # Set up stdin reader
            reader = asyncio.StreamReader()
            protocol = asyncio.StreamReaderProtocol(reader)
            await loop.connect_read_pipe(lambda: protocol, sys.stdin)
            
            # Set up stdout writer
            writer_transport, writer_protocol = await loop.connect_write_pipe(
                asyncio.streams.FlowControlMixin,
                asyncio.subprocess.PIPE
            )
            writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, loop)
            
            # Process messages
            while self.running:
                try:
                    # Read a line from stdin
                    line = await reader.readline()
                    if not line:
                        break
                    
                    # Parse the JSON-RPC message
                    try:
                        request = json.loads(line)
                        logger.debug(f"Received request: {request}")
                        
                        # Process the request
                        response = await self._process_request(request)
                        if response:
                            # Send the response
                            response_str = json.dumps(response) + "\n"
                            writer.write(response_str.encode('utf-8'))
                            await writer.drain()
                    
                    except json.JSONDecodeError as e:
                        error = self._create_error_response(
                            None, -32700, "Parse error", str(e))
                        writer.write((json.dumps(error) + "\n").encode('utf-8'))
                        await writer.drain()
                    
                    except Exception as e:
                        logger.error(f"Error processing request: {e}", exc_info=self.debug)
                        error = self._create_error_response(
                            None, -32603, "Internal error", str(e))
                        writer.write((json.dumps(error) + "\n").encode('utf-8'))
                        await writer.drain()
                
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in message loop: {e}", exc_info=self.debug)
                    await asyncio.sleep(0.1)  # Prevent tight loop on errors
        
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=self.debug)
            raise
        
        finally:
            self.running = False
            logger.info("FastMCP server stopped")
    
    async def stop(self) -> None:
        """Stop the server."""
        self.running = False
    
    def _handle_signal(self, signum, frame) -> None:
        """Handle OS signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.stop())
    
    async def _process_request(self, request: JsonRpcRequest) -> Optional[JsonRpcResponse]:
        """Process a JSON-RPC request."""
        try:
            # Validate the request
            if not isinstance(request, dict):
                return self._create_error_response(
                    None, -32600, "Invalid Request", "Request must be an object")
            
            jsonrpc = request.get("jsonrpc")
            if jsonrpc != "2.0":
                return self._create_error_response(
                    request.get("id"), -32600, "Invalid Request", "jsonrpc must be '2.0'")
            
            method = request.get("method")
            if not method or not isinstance(method, str):
                return self._create_error_response(
                    request.get("id"), -32600, "Invalid Request", "method is required and must be a string")
            
            # Find the request handler
            handler = self._request_handlers.get(method)
            if not handler:
                return self._create_error_response(
                    request.get("id"), -32601, "Method not found", f"Unknown method: {method}")
            
            # Call the handler
            try:
                params = request.get("params", {})
                result = await handler(params, request.get("id"))
                
                # Only send a response for notifications (where id is None)
                if "id" in request:
                    return {
                        "jsonrpc": "2.0",
                        "id": request["id"],
                        "result": result,
                    }
                
                return None
            
            except Exception as e:
                logger.error(f"Error handling {method}: {e}", exc_info=self.debug)
                return self._create_error_response(
                    request.get("id"), -32603, "Internal error", str(e))
        
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=self.debug)
            return self._create_error_response(
                request.get("id") if isinstance(request, dict) else None,
                -32603, "Internal error", str(e)
            )
    
    async def _handle_initialize(self, params: JsonRpcParams, request_id: JsonRpcId) -> Dict[str, Any]:
        """Handle the initialize request."""
        return {
            "serverInfo": {
                "name": "FastMCP 2.13 Server",
                "version": "2.13.0",
            },
            "capabilities": {
                "toolExecution": {"dynamicRegistration": True},
                "toolDiscovery": {"dynamicRegistration": True},
            },
        }
    
    async def _handle_tool_execute(self, params: JsonRpcParams, request_id: JsonRpcId) -> Dict[str, Any]:
        """Handle the tool/execute request."""
        if not isinstance(params, dict):
            raise ValueError("params must be an object")
        
        tool_name = params.get("name")
        if not tool_name or not isinstance(tool_name, str):
            raise ValueError("name is required and must be a string")
        
        tool_args = params.get("arguments", {})
        if not isinstance(tool_args, dict):
            raise ValueError("arguments must be an object")
        
        # Get the tool
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        # Execute the tool
        try:
            result = await tool(**tool_args)
            return {"result": result}
        
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=self.debug)
            raise ValueError(f"Tool execution failed: {str(e)}")
    
    async def _handle_tool_list(self, params: JsonRpcParams, request_id: JsonRpcId) -> Dict[str, Any]:
        """Handle the tool/list request."""
        tools = []
        
        for name, tool in self.get_tools().items():
            tools.append({
                "name": name,
                "description": getattr(tool, 'description', ''),
            })
        
        return {"tools": tools}
    
    async def _handle_tool_describe(self, params: JsonRpcParams, request_id: JsonRpcId) -> Dict[str, Any]:
        """Handle the tool/describe request."""
        if not isinstance(params, dict):
            raise ValueError("params must be an object")
        
        tool_name = params.get("name")
        if not tool_name or not isinstance(tool_name, str):
            raise ValueError("name is required and must be a string")
        
        # Get the tool
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        # Get the tool's definition
        tool_def = {
            "name": tool_name,
            "description": getattr(tool, 'description', ''),
            "parameters": getattr(tool, 'parameters', {}),
        }
        
        # Add additional metadata if available
        if hasattr(tool, '__doc__') and tool.__doc__:
            tool_def['documentation'] = inspect.cleandoc(tool.__doc__)
        
        return {"tool": tool_def}
    
    async def _handle_shutdown(self, params: JsonRpcParams, request_id: JsonRpcId) -> None:
        """Handle the shutdown request."""
        await self.stop()
        return None
    
    @staticmethod
    def _create_error_response(
        request_id: JsonRpcId,
        code: int,
        message: str,
        data: Any = None,
    ) -> JsonRpcResponse:
        """Create a JSON-RPC error response."""
        error = {
            "code": code,
            "message": message,
        }
        
        if data is not None:
            error["data"] = data
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error,
        }


def create_fastmcp_server(debug: bool = False) -> FastMCP13Server:
    """Create and configure a FastMCP 2.13 server.
    
    Args:
        debug: Whether to enable debug logging.
        
    Returns:
        A configured FastMCP13Server instance.
    """
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    
    # Create the server
    server = FastMCP13Server(debug=debug)
    
    # Discover and register tools
    from mcp_server.tool_discovery import register_tools
    register_tools(server)
    
    return server


async def main() -> int:
    """Main entry point for the FastMCP server."""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="FastMCP 2.13 Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Create and start the server
    server = create_fastmcp_server(debug=args.debug)
    
    try:
        await server.start()
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=args.debug)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
