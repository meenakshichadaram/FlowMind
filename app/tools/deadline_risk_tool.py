import math
from langchain_core.tools import tool

@tool
def deadline_risk_tool(hours_remaining: float, days_left: float, complexity: int, completion_rate: float) -> str:
    """Calculates completion probability and deadline risk score using task parameters and historical velocity."""
    hours_req = float(hours_remaining) * (1.0 + (float(complexity) - 3) * 0.1)
    daily_available = 4.0  # Default assumed student daily capacity
    total_available_hours = float(days_left) * daily_available * float(completion_rate)

    margin = total_available_hours - hours_req
    # Sigmoid completion probability
    prob = 1.0 / (1.0 + math.exp(-0.6 * margin))
    prob = round(max(0.05, min(0.98, prob)), 2)

    risk_score = round((1.0 - prob) * 100, 1)

    if risk_score > 70:
        level = "CRITICAL RISK"
    elif risk_score > 40:
        level = "MODERATE RISK"
    else:
        level = "LOW RISK"

    return (
        f"📊 Deadline Risk Analysis:\n"
        f"• Completion Probability: {int(prob * 100)}%\n"
        f"• Risk Score: {risk_score}/100 ({level})\n"
        f"• Required Work: {round(hours_req, 1)} hrs vs Estimated Available: {round(total_available_hours, 1)} hrs"
    )
