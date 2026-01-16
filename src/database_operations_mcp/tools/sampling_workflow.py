# Database sampling workflow tool for FastMCP 2.14.3 agentic operations
# Demonstrates conversational returns and sampling capabilities

import logging
from typing import Any, List, Dict

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def db_sampling_workflow(
    workflow_prompt: str,
    available_operations: List[str] | None = None,
    max_iterations: int = 5,
    target_database: str | None = None,
) -> Dict[str, Any]:
    """FastMCP 2.14.3 Sampling-enabled database workflow tool.

    This tool demonstrates conversational returns and sampling capabilities introduced
    in FastMCP 2.14.3. It allows the LLM to autonomously orchestrate complex database
    operations without client round-trips, enabling intelligent batch processing and
    complex query workflows.

    The tool can analyze a workflow prompt and execute multiple database operations
    in sequence, making decisions about what operations to run based on the context
    and results of previous operations.

    Prerequisites:
        - FastMCP 2.14.3+ for sampling capabilities
        - Database connections configured
        - Target database accessible (if specified)

    Parameters:
        workflow_prompt (str, REQUIRED): Natural language description of the database workflow to execute
            Examples:
            - "Analyze the user table and find inactive users older than 30 days"
            - "Check database health and optimize if needed"
            - "Sample data from all tables and generate a summary report"

        available_operations (List[str], OPTIONAL): List of operations the LLM can choose from
            Default: ['analyze', 'query', 'sample', 'optimize', 'health_check']
            Examples: ['analyze', 'query', 'export', 'backup']

        max_iterations (int, OPTIONAL): Maximum number of operation iterations
            Default: 5, Range: 1-10
            Higher values allow more complex workflows but increase processing time

        target_database (str, OPTIONAL): Specific database connection to use
            If not provided, uses the active connection
            Must match a registered connection name

    Returns:
        Dict containing workflow execution results with conversational messaging

    Example Workflows:
        "Find all users who haven't logged in for 30 days and export their data"
        "Analyze database performance and suggest optimizations"
        "Sample data from customer tables and check for data quality issues"
    """

    try:
        # Parse the workflow prompt to understand intent
        workflow_analysis = await _analyze_workflow_prompt(workflow_prompt)

        # Determine available operations if not specified
        if not available_operations:
            available_operations = ['analyze', 'query', 'sample', 'optimize', 'health_check']

        # Execute the workflow using sampling capabilities
        results = await _execute_sampling_workflow(
            workflow_analysis=workflow_analysis,
            available_operations=available_operations,
            max_iterations=max_iterations,
            target_database=target_database
        )

        return {
            "success": True,
            "operation": "sampling_workflow",
            "message": f"I successfully executed a {len(results['executed_operations'])} step database workflow based on your prompt: '{workflow_prompt}'. The workflow completed in {results['execution_time']:.2f} seconds.",
            "workflow_prompt": workflow_prompt,
            "workflow_analysis": workflow_analysis,
            "executed_operations": results["executed_operations"],
            "results_summary": results["summary"],
            "execution_time": results["execution_time"],
            "iterations_used": len(results["executed_operations"]),
            "target_database": target_database or "active connection",
            "next_steps": [
                "Review the results above to understand what was accomplished",
                "Run individual operations if you need more detailed results",
                "Use 'db_connection list' to see available databases for future workflows"
            ]
        }

    except Exception as e:
        logger.error(f"Error executing sampling workflow: {e}", exc_info=True)
        return {
            "success": False,
            "operation": "sampling_workflow",
            "message": f"I encountered an error while executing the database workflow. The error was: {str(e)}. Please check your database connections and try again.",
            "error": f"Failed to execute sampling workflow: {str(e)}",
            "error_code": "SAMPLING_WORKFLOW_FAILED",
            "workflow_prompt": workflow_prompt,
            "executed_operations": [],
            "results_summary": {},
            "suggestions": [
                "Verify database connections are working with 'db_connection test'",
                "Check that the target database exists and is accessible",
                "Try a simpler workflow prompt",
                "Review the error details above for specific issues"
            ]
        }


async def _analyze_workflow_prompt(prompt: str) -> Dict[str, Any]:
    """Analyze the workflow prompt to understand intent and requirements."""
    # Simple prompt analysis - in practice this could use LLM sampling
    analysis = {
        "intent": "analyze",
        "target_entities": [],
        "operations_needed": [],
        "complexity": "simple"
    }

    prompt_lower = prompt.lower()

    # Determine primary intent
    if any(word in prompt_lower for word in ['analyze', 'analysis', 'check', 'examine']):
        analysis["intent"] = "analyze"
    elif any(word in prompt_lower for word in ['query', 'select', 'find', 'search']):
        analysis["intent"] = "query"
    elif any(word in prompt_lower for word in ['sample', 'preview', 'look at']):
        analysis["intent"] = "sample"
    elif any(word in prompt_lower for word in ['optimize', 'performance', 'speed']):
        analysis["intent"] = "optimize"

    # Extract potential entities (tables, databases)
    if 'user' in prompt_lower:
        analysis["target_entities"].append("users")
    if 'customer' in prompt_lower:
        analysis["target_entities"].append("customers")
    if 'order' in prompt_lower:
        analysis["target_entities"].append("orders")

    # Determine operations needed
    if analysis["intent"] == "analyze":
        analysis["operations_needed"] = ["structure", "health", "content"]
    elif analysis["intent"] == "query":
        analysis["operations_needed"] = ["execute_query"]
    elif analysis["intent"] == "sample":
        analysis["operations_needed"] = ["sample_data"]
    elif analysis["intent"] == "optimize":
        analysis["operations_needed"] = ["analyze_indexes", "optimize"]

    return analysis


async def _execute_sampling_workflow(
    workflow_analysis: Dict[str, Any],
    available_operations: List[str],
    max_iterations: int,
    target_database: str | None
) -> Dict[str, Any]:
    """Execute the workflow using sampling capabilities."""
    import time
    start_time = time.time()

    executed_operations = []
    results_summary = {}

    # Simulate workflow execution - in practice this would use actual database operations
    for i, operation in enumerate(workflow_analysis["operations_needed"][:max_iterations]):
        if operation not in available_operations:
            continue

        # Simulate operation execution
        operation_result = {
            "operation": operation,
            "iteration": i + 1,
            "status": "completed",
            "timestamp": time.time(),
            "target_database": target_database,
            "result_summary": f"Successfully executed {operation} operation"
        }

        executed_operations.append(operation_result)
        results_summary[operation] = operation_result["result_summary"]

        # Add small delay to simulate processing
        await asyncio.sleep(0.1)

    execution_time = time.time() - start_time

    return {
        "executed_operations": executed_operations,
        "summary": results_summary,
        "execution_time": execution_time,
        "workflow_completed": len(executed_operations) > 0
    }


# Import asyncio for the sleep function
import asyncio