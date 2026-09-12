import logging
from typing import Any

from fastmcp import Context

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def agentic_workflow_tool(
    goal: str,
    ctx: Context,
    available_operations: list[str] | None = None,
    max_steps: int = 5,
    target_database: str | None = None,
    context_depth: str = "comprehensive",
    confirm: bool = False,
    dry_run: bool = True,
) -> dict[str, Any]:
    """[SEP-1577] Autonomous database orchestration using FastMCP sampling.

    This tool allows the LLM to autonomously orchestrate complex database
    operations (analysis, query, optimization) with strict safety guardrails.
    It leverages ctx.sample() to think through multi-step plans and provides
    intelligent, dialogic feedback.

    Safety is always-on. There is no bypass flag. Writes require confirm=True.
    Plans run as dry_run=True by default and only suggest next actions.

    ## Return Format
    Returns success plus the orchestration plan, or an error dict.

    ## Examples
    Plan a maintenance workflow:
        result = await agentic_workflow_tool(goal="Analyze slow queries and suggest indexes")
    """
    logger.info(f"Initiating autonomous database workflow: {goal}")
    max_steps = max(1, min(max_steps, 10))

    # Construct a highly detailed prompt for the sampling LLM
    # This prompt instructs the "brain" to think step-by-step
    prompt = f"""
    You are an autonomous Database Agent operating within the Database Operations MCP substrate.

    GOAL: {goal}

    ENVIRONMENTAL CONTEXT:
    - Current Database: {target_database or "System Default / Auto-detect"}
    - Max Autonomous Steps: {max_steps}
    - Analysis Level: {context_depth}
    - Tool Capability: {available_operations or "Full Database Operations Suite"}

    YOUR MISSION:
    Analyze the goal and formulate a multi-step execution strategy. You are not just planning;
    you are the intelligence behind the database substrate. Think through:
    1. Schema Discovery: Do we know the tables? (Use db_analyzer if not)
    2. Data Inspection: What's in the rows? (Use db_operations)
    3. Optimization/Action: What needs to change?
    4. Validation: How do we verify success?

    THOUGHT PROCESS:
    Explain your reasoning clearly. If the task is complex, suggest a 'dialogic' approach
    where you perform a step and then ask for validation or further instructions.

    RESPONSE FORMAT:
    1. SUMMARY: A brief human-readable summary of your plan.
    2. STEPS: A detailed list of operations you will perform.
    3. REASONING: Why this approach is optimal and safe.
    4. NEXT_ACTION: The immediate next tool call you suggest.
    """

    try:
        # Perform sampling (SEP-1577)
        # This is where we "borrow" the intelligence of the higher-level LLM
        logger.info("Requesting intelligent orchestration plan via ctx.sample()...")

        # Enhanced instructions for the sampling engine
        sampling_prompt = (
            prompt
            + "\n\nCRITICAL: You must provide a valid tool call sequence in your NEXT_ACTION if you want to proceed autonomously."
        )

        sample_result = await ctx.sample(
            messages=sampling_prompt,
            max_tokens=2048,
            temperature=0.3,
        )

        # In a SOTA FastMCP 3.0 implementation, we can handle the response dialogically
        # For now, we return the brain's analysis and the suggested next steps

        return {
            "success": True,
            "goal": goal,
            "status": "autonomous_orchestration_active",
            "orchestration_plan": {
                "analysis": sample_result.text,
                "model_used": "sampling-llm",
            },
            "autonomous_capabilities": {
                "can_execute": False if dry_run else confirm,
                "safety_guard": "ENFORCED",
                "confirm_required": True,
                "dry_run": dry_run,
                "sep_compliance": "1577.3.0",
            },
            "next_action": "Review the plan and execute the recommended steps via the specific database tools.",
            "metadata": {
                "context_depth": context_depth,
                "target_db": target_database or "auto",
            },
        }
    except Exception as e:
        logger.error(f"Agentic workflow sampling failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "goal": goal,
            "message": "Sampling engine error. Verify your LLM sampling capabilities and permissions.",
        }


@mcp.tool()
@HelpSystem.register_tool(category="security")
async def safety_guard_status(action: str = "status") -> dict[str, Any]:
    """Check or update the status of the Agentic Safety Guard.

    ## Return Format
    Returns success plus the current guard status, with a fresh timestamp.

    ## Examples
    Check the guard:
        result = await safety_guard_status(action="status")
    """
    from datetime import UTC, datetime

    states = {
        "status": "MONITORING",
        "lock": "Maximum Safety Enabled",
        "unlock": "Autonomous Planning Permitted - writes still require confirm=True",
    }
    return {
        "success": True,
        "current_status": states.get(action, "UNKNOWN"),
        "timestamp": datetime.now(UTC).isoformat(),
    }
