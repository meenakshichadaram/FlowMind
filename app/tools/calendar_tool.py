from langchain_core.tools import tool
from datetime import datetime, timedelta

@tool
def calendar_tool(available_hours_per_day: float, days_ahead: int = 5) -> str:
    """Calculates available study time windows over upcoming days based on student calendar constraints."""
    today = datetime.now()
    schedule = []
    total = 0.0

    for i in range(days_ahead):
        day_date = today + timedelta(days=i)
        day_str = day_date.strftime("%Y-%m-%d (%A)")
        hours = available_hours_per_day if day_date.weekday() < 5 else available_hours_per_day * 1.2
        hours = round(hours, 1)
        total += hours
        schedule.append(f"📅 {day_str}: {hours} study hours available")

    return f"Available Study Schedule (Total: {round(total, 1)} hrs over {days_ahead} days):\n" + "\n".join(schedule)
