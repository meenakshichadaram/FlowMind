from langchain_core.tools import tool
import json

@tool
def task_breakdown_tool(task_description: str, estimated_hours: float) -> str:
    """Breaks down a complex assignment or project task into actionable micro-steps with time estimates."""
    est = float(estimated_hours)
    step_count = max(2, min(6, int(est / 1.5)))
    chunk = round(est / step_count, 1)

    steps = [
        f"1. Context Retrieval & Setup: Gather resources and outline requirements ({chunk} hrs)",
        f"2. Core Implementation / Writing: Execute main deliverables ({chunk} hrs)",
        f"3. Debugging & Self-Review: Test code or proofread draft ({chunk} hrs)",
        f"4. Final Integration & Submission Prep: Polish formatting and verify criteria ({round(est - (chunk*(step_count-1)), 1)} hrs)"
    ]

    return f"Task Breakdown for '{task_description}' ({estimated_hours} total hours):\n" + "\n".join(steps[:step_count])
