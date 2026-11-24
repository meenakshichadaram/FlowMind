from langchain_core.tools import tool

@tool
def focus_score_tool(duration_mins: int, distractions: int, tab_switches: int) -> str:
    """Calculates focus score (0-100) and outputs session recommendations based on distraction frequency."""
    dur = float(duration_mins)
    dist = float(distractions)
    tabs = float(tab_switches)

    base = 100.0
    distraction_penalty = dist * 8.0
    tab_penalty = (tabs / (dur / 10.0 or 1.0)) * 3.0

    score = max(10.0, min(100.0, base - distraction_penalty - tab_penalty))
    score = round(score, 1)

    if score >= 80:
        state = "Peak Hyperfocus"
        rec = "Maintain current environment. Take a 5-minute hydration break after 50 minutes."
    elif score >= 50:
        state = "Moderate Distraction"
        rec = "Close unused browser tabs and mute non-essential messaging apps."
    else:
        state = "High Focus Loss / Fatigue"
        rec = "High distraction rate detected. Take an immediate 15-minute screen-free rest break."

    return (
        f"🎯 Focus Audit Score: {score}/100 ({state})\n"
        f"• Duration: {duration_mins} mins | Distractions: {distractions} | Tab Switches: {tab_switches}\n"
        f"• Recommendation: {rec}"
    )
