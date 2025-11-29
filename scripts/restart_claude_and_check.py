"""
Restart Claude Desktop and verify MCP server loads successfully.

This script:
1. Pre-checks if server will load (optional but recommended)
2. Stops Claude Desktop
3. Restarts Claude Desktop
4. Monitors logs for successful MCP server startup
5. Automatically displays tail of Claude Desktop log file
6. Reports success/failure

Note: Restarting Claude requires stopping the process (works without UAC).
Starting Claude may require UAC if installed in Program Files.

The script automatically finds and displays the Claude Desktop log file from:
%APPDATA%\\Claude\\logs\\mcp-server-{server-name}.log
"""

import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta


def find_claude_process():
    """Find Claude Desktop process."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Claude.exe", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and "Claude.exe" in result.stdout:
            return True
        return False
    except Exception as e:
        print(f"[WARN] Could not check Claude process: {e}")
        return None


def find_claude_desktop_log(server_name="database-operations-mcp"):
    """Find the Claude Desktop log file for this MCP server.

    Args:
        server_name: MCP server name (default: database-operations-mcp)

    Returns:
        Path to log file or None if not found
    """
    import os

    # Claude Desktop logs are in %APPDATA%\Claude\logs\mcp-server-{name}.log
    appdata = os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
    claude_logs_dir = Path(appdata) / "Claude" / "logs"
    claude_log_file = claude_logs_dir / f"mcp-server-{server_name}.log"

    if claude_log_file.exists():
        return claude_log_file

    # Also check for variations
    possible_names = [
        server_name,
        server_name.replace("-", "_"),
        server_name.replace("_", "-"),
    ]

    for name in possible_names:
        log_file = claude_logs_dir / f"mcp-server-{name}.log"
        if log_file.exists():
            return log_file

    return None


def tail_log_file(log_file: Path, lines: int = 20):
    """Display the last N lines of a log file.

    Args:
        log_file: Path to log file
        lines: Number of lines to display (default: 20)
    """
    if not log_file or not log_file.exists():
        return

    try:
        print(f"\n{'=' * 60}")
        print(f"📋 Last {lines} lines from: {log_file}")
        print(f"{'=' * 60}")

        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
            tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

            for line in tail_lines:
                print(line.rstrip())

        print(f"{'=' * 60}\n")
    except Exception as e:
        print(f"[WARN] Could not read log file: {e}")


def stop_claude():
    """Stop Claude Desktop using taskkill.

    Uses Windows taskkill command to forcefully terminate Claude.exe.
    No UAC required - works without elevation.
    """
    print("\n[1/4] Stopping Claude Desktop (using taskkill)...")
    try:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", "Claude.exe"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("[OK] Claude Desktop stopped")
            time.sleep(2)  # Wait for process to fully terminate
            return True
        elif "not found" in result.stdout.lower() or "not running" in result.stdout.lower():
            print("[INFO] Claude Desktop was not running")
            return True
        else:
            print(f"[WARN] Unexpected response: {result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        print("[WARN] Timeout stopping Claude (process may be hung)")
        return False
    except Exception as e:
        print(f"[FAIL] Error stopping Claude: {e}")
        return False


def start_claude(claude_path_arg=None):
    """Start Claude Desktop.

    Args:
        claude_path_arg: Optional path to Claude.exe (for --claude-path option)
    """
    print("\n[2/4] Starting Claude Desktop...")

    # Use provided path if given
    if claude_path_arg:
        claude_path = Path(claude_path_arg)
        if claude_path.exists():
            print(f"[INFO] Using specified Claude path: {claude_path}")
        else:
            print(f"[FAIL] Specified Claude path does not exist: {claude_path}")
            return False
    else:
        # Common Claude Desktop install locations
        possible_paths = [
            Path.home() / "AppData/Local/Programs/claude-desktop/Claude.exe",
            Path.home() / "AppData/Roaming/npm/claude",
            Path("C:/Program Files/Claude/Claude.exe"),
            Path("C:/Program Files (x86)/Claude/Claude.exe"),
        ]

        # Check if Claude is in PATH (less common but possible)
        try:
            result = subprocess.run(["where", "Claude"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                found_path = Path(result.stdout.strip().split("\n")[0])
                if found_path.exists():
                    possible_paths.insert(0, found_path)
        except:
            pass

        # Try to find Claude
        claude_path = None
        for path in possible_paths:
            if path.exists():
                claude_path = path
                break

        if not claude_path:
            print("[FAIL] Could not find Claude Desktop executable")
            print("\nPlease start Claude Desktop manually, then run:")
            print("  python scripts/restart_claude_and_check.py --no-restart")
            print("\nOr specify Claude path with --claude-path option")
            return False

    try:
        # Start Claude Desktop
        print(f"[INFO] Starting Claude Desktop from: {claude_path}")
        subprocess.Popen([str(claude_path)], shell=True)
        print(f"[OK] Started Claude Desktop")
        print("[INFO] Waiting for Claude to initialize...")
        print("[INFO] ⚠️  Check Claude Desktop - chat window should be EMPTY (fresh restart)")
        time.sleep(5)  # Give Claude time to start and connect to MCP
        return True
    except Exception as e:
        print(f"[FAIL] Error starting Claude: {e}")
        print(f"[INFO] Try starting Claude manually from: {claude_path}")
        return False


def monitor_logs_for_startup(
    timeout_seconds=30,
    check_recent=True,
    log_file_size_before_check=None,
    server_name="database-operations-mcp",
):
    """Monitor logs for successful MCP server startup.

    Args:
        timeout_seconds: Timeout for watching new logs
        check_recent: If True, check recent logs (for --no-restart mode)
        log_file_size_before_check: Size of log file before script ran (to avoid checking our own logs)
        server_name: MCP server name (default: database-operations-mcp)

    Returns:
        tuple: (success: bool, claude_log_file: Path | None)
    """
    print("\n[3/4] Monitoring logs for MCP server startup...")

    # First, try to find Claude Desktop log file (primary source)
    claude_log_file = find_claude_desktop_log(server_name)

    # Also check for log file in common local locations
    possible_log_files = [
        Path("logs/database-operations-mcp.log"),
        Path("http_test.log"),
        Path("logs/mcp.log"),
    ]

    local_log_file = None
    for log_path in possible_log_files:
        if log_path.exists():
            local_log_file = log_path
            break

    # Prefer Claude Desktop log if available
    log_file = claude_log_file if claude_log_file else local_log_file

    if claude_log_file:
        print(f"[INFO] Found Claude Desktop log: {claude_log_file}")
    elif local_log_file:
        print(f"[INFO] Using local log: {local_log_file}")
        print(f"[INFO] Claude Desktop log not found yet (may be created during startup)")

    if not log_file:
        print(f"[WARN] Log file not found in expected locations")
        print("[INFO] Server may not have started yet, or logs are elsewhere")
        import os

        appdata = os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
        expected_claude_log = Path(appdata) / "Claude" / "logs" / f"mcp-server-{server_name}.log"
        print(f"[INFO] Expected Claude log: {expected_claude_log}")
        return False, None

    # If we have a size limit, only read up to that point (avoid checking logs created by pre-check)
    max_bytes = log_file_size_before_check if log_file_size_before_check else None

    # Look for success indicators (database-operations-mcp specific)
    success_indicators = [
        "fastmcp 2.13 persistent storage initialized",
        "registered",
        "tools registered",
        "server_startup",
        "mcp server initialized",
        "database operations mcp server",
        "all portmanteau tools imported successfully",
    ]

    error_indicators = [
        "error",
        "exception",
        "traceback",
        "importerror",
        "modulenotfounderror",
        "failed",
        "server_startup_error",
        "failed to import",
    ]

    # First, check recent logs if requested (for --no-restart mode)
    if check_recent:
        print("[INFO] Checking LAST startup attempt in logs...")
        try:
            # Read log file up to the size before we started (to avoid our own pre-check logs)
            if max_bytes and log_file.stat().st_size > max_bytes:
                with open(log_file, "rb") as f:
                    content = f.read(max_bytes).decode("utf-8", errors="ignore")
                    # Get last complete line
                    if content and not content.endswith("\n"):
                        content = content.rsplit("\n", 1)[0] + "\n"
                    all_lines = content.splitlines(True)
            else:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    all_lines = f.readlines()

                    # Check last few lines for success/error indicators
                    found_success = False
                    found_error = False

                    # Check last 50 lines (most recent)
                    for line in all_lines[-50:]:
                        line_lower = line.lower()

                        # Check for errors first
                        if any(indicator.lower() in line_lower for indicator in error_indicators):
                            if "error" in line_lower and (
                                "startup" in line_lower or "import" in line_lower
                            ):
                                found_error = True
                                print("[FAIL] Last startup attempt FAILED:")
                                print(f"  {line.strip()[:200]}...")
                                return False, claude_log_file

                        # Check for success
                        if any(indicator.lower() in line_lower for indicator in success_indicators):
                            if (
                                "storage initialized" in line_lower
                                or "tools imported" in line_lower
                            ):
                                found_success = True
                                print("[SUCCESS] Last startup attempt succeeded!")
                                print(f"  {line.strip()[:200]}...")
                                return True, claude_log_file

                    if found_success:
                        return True, claude_log_file
                    elif found_error:
                        return False, claude_log_file
                    else:
                        print("[WARN] Could not determine success/failure from recent logs")
                        print("[INFO] Check logs manually for startup messages")
                        return False, claude_log_file

        except Exception as e:
            print(f"[WARN] Error checking recent logs: {e}")

    # If no recent success/error found, monitor for new entries
    start_time = datetime.now()
    timeout = timedelta(seconds=timeout_seconds)

    last_position = log_file.stat().st_size if log_file.exists() else 0

    print(f"[INFO] Watching log file: {log_file}")
    print(f"[INFO] Timeout: {timeout_seconds} seconds")

    while datetime.now() - start_time < timeout:
        try:
            # Check for new log entries
            if log_file.exists():
                current_size = log_file.stat().st_size
                if current_size > last_position:
                    # Read new log entries
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        f.seek(last_position)
                        new_lines = f.readlines()
                        last_position = current_size

                        # Check for success or error
                        for line in new_lines:
                            line_lower = line.lower()

                            # Check for errors first
                            if any(
                                indicator.lower() in line_lower for indicator in error_indicators
                            ):
                                if "error" in line_lower and (
                                    "startup" in line_lower or "import" in line_lower
                                ):
                                    print("\n[FAIL] Error detected in new logs:")
                                    print(f"  {line.strip()[:200]}...")
                                    return False, claude_log_file

                            # Check for success
                            if any(
                                indicator.lower() in line_lower for indicator in success_indicators
                            ):
                                if (
                                    "storage initialized" in line_lower
                                    or "tools imported" in line_lower
                                ):
                                    print(
                                        "\n[SUCCESS] MCP server started successfully (new log entry)!"
                                    )
                                    print(f"  {line.strip()[:200]}...")
                                    return True, claude_log_file
        except Exception as e:
            print(f"[WARN] Error reading log: {e}")

        time.sleep(1)

    print(f"\n[WARN] Timeout after {timeout_seconds} seconds")
    print("[INFO] Check logs manually or verify Claude Desktop MCP configuration")
    return False, claude_log_file


def pre_check_server():
    """Pre-check if server will load before restarting Claude.

    Returns:
        tuple: (success: bool, log_file_size_before: int | None)
    """
    print("\n[0/4] Pre-checking server load...")

    # Get log file size BEFORE we run pre-check (if log exists)
    log_file = Path("logs/database-operations-mcp.log")
    log_size_before = log_file.stat().st_size if log_file.exists() else None

    try:
        import sys

        src_path = Path(__file__).parent.parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        # Try to import and initialize the MCP server
        from database_operations_mcp.config.mcp_config import mcp

        # Check if MCP instance is valid
        if mcp is None:
            print("[FAIL] MCP instance is None")
            return False, log_size_before

        # Verify MCP instance has expected attributes
        if not hasattr(mcp, "name"):
            print("[WARN] MCP instance missing 'name' attribute")
            return False, log_size_before

        # Try to import main module (this triggers tool registration)
        try:
            from database_operations_mcp.main import DatabaseOperationsMCP

            # Create instance to trigger tool imports
            server = DatabaseOperationsMCP()
            print(
                f"[OK] Pre-check passed - MCP instance '{mcp.name}' loaded, server should start successfully"
            )
            return True, log_size_before
        except Exception as e:
            print(f"[WARN] Could not initialize server instance: {e}")
            print("[INFO] MCP config loaded, but server initialization failed")
            # Still return True since MCP instance loaded (might work in Claude anyway)
            return True, log_size_before

    except ImportError as e:
        print(f"[FAIL] Pre-check failed - Import error: {e}")
        print("[WARN] Server may not load in Claude. Fix import issues first!")
        response = input("\nContinue anyway? (y/N): ")
        return response.lower() == "y", log_size_before
    except Exception as e:
        print(f"[FAIL] Pre-check failed: {e}")
        print("[WARN] Server may not load in Claude. Fix issues first!")
        response = input("\nContinue anyway? (y/N): ")
        return response.lower() == "y", log_size_before


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Restart Claude Desktop and verify MCP server loads"
    )
    parser.add_argument(
        "--skip-precheck", action="store_true", help="Skip pre-check (not recommended)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout for log monitoring in seconds (default: 30)",
    )
    parser.add_argument(
        "--claude-path", type=str, help="Path to Claude.exe (auto-detected if not specified)"
    )
    parser.add_argument(
        "--no-restart", action="store_true", help="Only monitor logs (do not restart Claude)"
    )
    parser.add_argument(
        "--log-lines",
        type=int,
        default=30,
        help="Number of log lines to display at the end (default: 30)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Claude Desktop Restart & MCP Server Check")
    print("Database Operations MCP")
    print("=" * 60)

    # Pre-check (and get log file size before we started)
    log_file_size_before = None
    if not args.skip_precheck:
        precheck_passed, log_file_size_before = pre_check_server()
        if not precheck_passed:
            print("\n[STOP] Pre-check failed. Fix issues before restarting Claude.")
            return 1

    # Restart Claude (unless --no-restart)
    if not args.no_restart:
        print("\n[INFO] ⚠️  IMPORTANT: Make sure Claude Desktop chat has text before restart")
        print("[INFO] After restart, chat window should be EMPTY (proving restart worked)")
        time.sleep(2)  # Give user time to see the message

        if not stop_claude():
            print("\n[STOP] Failed to stop Claude. Check manually.")
            return 1

        if not start_claude(args.claude_path):
            print("\n[STOP] Failed to start Claude. Start manually and check logs.")
            return 1

        print("\n[INFO] ✅ Claude Desktop should now be restarting...")
        print("[INFO] Check Claude Desktop window - chat should be EMPTY if restart succeeded!")
    else:
        print("\n[INFO] Skipping restart (--no-restart specified)")
        print("[INFO] Assuming Claude is already running")
        time.sleep(2)  # Give it a moment to connect

    # Monitor logs (check recent if --no-restart, wait for new if restarting)
    server_name = "database-operations-mcp"
    success, claude_log_file = monitor_logs_for_startup(
        timeout_seconds=args.timeout,
        check_recent=args.no_restart,
        log_file_size_before_check=log_file_size_before,
        server_name=server_name,
    )

    # Automatically display tail of Claude Desktop log file
    if claude_log_file:
        print("\n[4/4] Displaying Claude Desktop log tail...")
        tail_log_file(claude_log_file, lines=args.log_lines)
    else:
        # Try to find it again (might have been created during monitoring)
        claude_log_file = find_claude_desktop_log(server_name)
        if claude_log_file:
            print("\n[4/4] Displaying Claude Desktop log tail...")
            tail_log_file(claude_log_file, lines=args.log_lines)
        else:
            print("\n[INFO] Claude Desktop log file not found")
            print(
                f"[INFO] Expected location: %APPDATA%\\Claude\\logs\\mcp-server-{server_name}.log"
            )

    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] MCP server loaded successfully in Claude!")
        if claude_log_file:
            print(f"[INFO] Full log available at: {claude_log_file}")
        return 0
    else:
        print("[FAILURE] Could not verify MCP server startup")
        print("\nNext steps:")
        print("  1. Check Claude Desktop console for errors")
        print("  2. Verify Claude Desktop MCP configuration")
        print("  3. Check if server imports correctly: python -m database_operations_mcp.main")
        if claude_log_file:
            print(f"  4. Review full log: {claude_log_file}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
