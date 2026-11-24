"""
Unified Intelligence Orchestrator
----------------------------------
This is the "brain" behind FlowMind's single-assistant product experience.

It does NOT replace or rewrite the four underlying engines (Intent Recovery,
Deadline Intelligence, Knowledge Fusion, Focus Intelligence). Instead, it sits
on top of them and the shared MemoryManager, fuses their signals together,
and produces the kind of "what should I do right now, and why" output a
student expects from a single intelligent assistant rather than four
disconnected dashboards.

Everything here is deterministic and fast (no LLM calls) so the Home screen
can render instantly. Each underlying engine can still be invoked explicitly
by the user for a deeper, LLM-reasoned explanation.
"""

import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.memory.memory_manager import MemoryManager
from app.database.models import UnfinishedActivity, DeadlineTask, FocusSession, ConceptLink


# Rough baseline "typical time to finish" per source type, used only to turn
# progress% into a human, minute-level estimate on the home screen.
_BASELINE_MINUTES = {
    "PDF": 45,
    "Video": 40,
    "Article": 25,
    "App": 20,
    "Code": 90,
    "Note": 15,
}


def _minutes_remaining(activity: UnfinishedActivity) -> int:
    baseline = _BASELINE_MINUTES.get(activity.source_type, 30)
    remaining_fraction = max(0.05, (100.0 - (activity.progress_percent or 0.0)) / 100.0)
    return max(5, round(baseline * remaining_fraction))


def humanize_timedelta(dt: Optional[datetime], now: Optional[datetime] = None) -> str:
    """Turns a datetime into 'just now', '3 hours ago', '12 days ago', etc."""
    if not dt:
        return "recently"
    now = now or datetime.utcnow()
    delta = now - dt
    seconds = delta.total_seconds()
    if seconds < 60:
        return "just now"
    minutes = seconds / 60
    if minutes < 60:
        return f"{int(minutes)} minute{'s' if minutes >= 2 else ''} ago"
    hours = minutes / 60
    if hours < 24:
        return f"{int(hours)} hour{'s' if hours >= 2 else ''} ago"
    days = hours / 24
    if days < 14:
        return f"{int(days)} day{'s' if days >= 2 else ''} ago"
    weeks = days / 7
    return f"{int(weeks)} week{'s' if weeks >= 2 else ''} ago"


def humanize_deadline(due_date: datetime, now: Optional[datetime] = None) -> str:
    now = now or datetime.utcnow()
    delta = due_date - now
    hours = delta.total_seconds() / 3600
    if hours <= 0:
        return "overdue"
    if hours < 48:
        return f"{int(hours)} hours"
    days = hours / 24
    return f"{int(round(days))} days"


class IntelligenceOrchestrator:
    """Fuses Intent Recovery, Deadline Intelligence, Knowledge Fusion and
    Focus Intelligence signals into one coherent 'what matters right now'
    picture for the Home / Intelligence Center screen."""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.memory = MemoryManager(db_session)

    # ------------------------------------------------------------------
    # Greeting + situation summary
    # ------------------------------------------------------------------
    def greeting(self) -> str:
        hour = datetime.now().hour
        if hour < 12:
            return "Good Morning"
        if hour < 17:
            return "Good Afternoon"
        return "Good Evening"

    def situation_bullets(self, user_id: int = 1) -> List[str]:
        now = datetime.utcnow()
        unfinished = self.memory.get_unfinished_activities(user_id=user_id, limit=20)
        deadlines = self.memory.get_deadline_tasks(user_id=user_id)
        focus_sessions = self.memory.get_recent_focus_sessions(user_id=user_id, limit=15)

        bullets: List[str] = []

        if unfinished:
            bullets.append(
                f"You have {len(unfinished)} unfinished learning task{'s' if len(unfinished) != 1 else ''} waiting on you."
            )

        upcoming = [d for d in deadlines if d.due_date > now]
        if upcoming:
            soonest = min(upcoming, key=lambda d: d.due_date)
            bullets.append(
                f"**{soonest.title}** closes in {humanize_deadline(soonest.due_date, now)}."
            )

        if unfinished:
            stalest = max(unfinished, key=lambda u: (now - (u.last_accessed or now)).total_seconds())
            days_inactive = (now - (stalest.last_accessed or now)).days
            if days_inactive >= 2:
                bullets.append(
                    f"Your **{stalest.title}** has been inactive for {days_inactive} day{'s' if days_inactive != 1 else ''}."
                )

        # Closest-to-done unfinished item
        if unfinished:
            closest = max(unfinished, key=lambda u: u.progress_percent or 0.0)
            if (closest.progress_percent or 0) >= 55:
                mins = _minutes_remaining(closest)
                bullets.append(
                    f"You're only about {mins} minutes away from finishing **{closest.title}**."
                )

        completion_probability = self._today_completion_probability(deadlines, focus_sessions)
        bullets.append(f"Today's study completion probability is **{completion_probability}%**.")

        return bullets[:5]

    def _today_completion_probability(
        self, deadlines: List[DeadlineTask], focus_sessions: List[FocusSession]
    ) -> int:
        """A light, deterministic blend of recent focus performance and
        deadline pressure, presented as a single confidence percentage."""
        avg_focus = (
            sum(f.focus_score for f in focus_sessions) / len(focus_sessions)
            if focus_sessions else 75.0
        )
        avg_risk = (
            sum(d.risk_score for d in deadlines) / len(deadlines)
            if deadlines else 25.0
        )
        score = (avg_focus * 0.65) + ((100 - avg_risk) * 0.35)
        return int(max(35, min(97, round(score))))

    # ------------------------------------------------------------------
    # Today's Focus: the single primary recommendation
    # ------------------------------------------------------------------
    def primary_recommendation(self, user_id: int = 1) -> Dict[str, Any]:
        now = datetime.utcnow()
        unfinished = self.memory.get_unfinished_activities(user_id=user_id, limit=20)
        deadlines = self.memory.get_deadline_tasks(user_id=user_id)

        candidates: List[Dict[str, Any]] = []

        for d in deadlines:
            if d.due_date <= now:
                continue
            hours_left = max(0.1, (d.due_date - now).total_seconds() / 3600)
            urgency = min(100.0, d.risk_score + (200.0 / hours_left if hours_left < 72 else 0))
            daily_capacity_minutes = 60  # a focused first session
            session_minutes = int(min(90, max(20, (d.estimated_hours_remaining * 60) / max(1, math.ceil(hours_left / 24)))))
            candidates.append({
                "kind": "deadline",
                "title": d.title,
                "urgency": urgency,
                "estimated_minutes": session_minutes,
                "reason": (
                    f"{d.course_or_project} is due in {humanize_deadline(d.due_date, now)} and is currently "
                    f"tracking at a {int(d.risk_score)}/100 risk score \u2014 starting a focused session now "
                    f"keeps it off the critical path."
                ),
                "cta": "Start a focused session",
            })

        for u in unfinished:
            days_inactive = (now - (u.last_accessed or now)).total_seconds() / 86400.0
            urgency = (u.priority_score or 50.0) + min(15.0, days_inactive * 1.5)
            candidates.append({
                "kind": "unfinished",
                "title": u.title,
                "urgency": urgency,
                "estimated_minutes": _minutes_remaining(u),
                "reason": (
                    u.importance_reason
                    or f"You're {int(u.progress_percent)}% through this and it's been waiting {int(days_inactive)} day(s)."
                ) + (f" Revisited {u.revisit_count} times \u2014 it clearly still matters." if u.revisit_count and u.revisit_count > 1 else ""),
                "cta": u.recommended_action or "Resume",
            })

        if not candidates:
            return {
                "title": "You're fully caught up",
                "estimated_minutes": 0,
                "reason": "No unfinished activities or upcoming deadlines are currently tracked in memory.",
                "cta": "Add a new goal or upload a document to get started.",
                "kind": "empty",
            }

        best = max(candidates, key=lambda c: c["urgency"])
        return best

    # ------------------------------------------------------------------
    # Recovered Intentions preview
    # ------------------------------------------------------------------
    def recovered_intentions(self, user_id: int = 1, limit: int = 3) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        unfinished = self.memory.get_unfinished_activities(user_id=user_id, limit=20)
        ordered = sorted(
            unfinished,
            key=lambda u: (now - (u.last_accessed or now)).total_seconds(),
            reverse=True,
        )
        out = []
        for u in ordered[:limit]:
            out.append({
                "title": u.title,
                "source_type": u.source_type,
                "last_accessed": u.last_accessed,
                "last_accessed_human": humanize_timedelta(u.last_accessed, now),
                "suggested_action": u.recommended_action or "Resume where you left off",
                "estimated_minutes": _minutes_remaining(u),
                "progress_percent": u.progress_percent or 0.0,
                "revisit_count": u.revisit_count or 0,
            })
        return out

    # ------------------------------------------------------------------
    # Deadline Radar preview
    # ------------------------------------------------------------------
    def deadline_radar(self, user_id: int = 1, limit: int = 4) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        deadlines = self.memory.get_deadline_tasks(user_id=user_id)
        user = self.memory.get_user_profile(user_id)
        daily_capacity = user.daily_goal_hours if user else 4.0

        rows = []
        for d in sorted(deadlines, key=lambda x: x.risk_score, reverse=True)[:limit]:
            days_left = max(0.5, (d.due_date - now).total_seconds() / 86400.0)
            est_completion_days = math.ceil(d.estimated_hours_remaining / max(0.5, daily_capacity))
            if d.risk_score > 70:
                risk_label = "Critical"
            elif d.risk_score > 40:
                risk_label = "Elevated"
            else:
                risk_label = "On Track"
            rows.append({
                "title": d.title,
                "course_or_project": d.course_or_project,
                "risk_score": d.risk_score,
                "risk_label": risk_label,
                "completion_probability": d.completion_probability,
                "estimated_completion": f"{est_completion_days} day{'s' if est_completion_days != 1 else ''}",
                "due_in": humanize_deadline(d.due_date, now),
                "id": d.id,
            })
        return rows

    # ------------------------------------------------------------------
    # Knowledge Journey preview (a connected concept chain)
    # ------------------------------------------------------------------
    def knowledge_chain(self, limit: int = 6) -> List[str]:
        links: List[ConceptLink] = self.memory.get_concept_links()
        if not links:
            return ["Machine Learning", "Linear Regression", "Loss Function", "Gradient Descent", "Optimization"]

        adjacency: Dict[str, List[str]] = {}
        incoming = set()
        for link in links:
            adjacency.setdefault(link.source_concept, []).append(link.target_concept)
            incoming.add(link.target_concept)

        roots = [n for n in adjacency.keys() if n not in incoming]
        start = roots[0] if roots else links[0].source_concept

        chain = [start]
        visited = {start}
        current = start
        while len(chain) < limit:
            nexts = [n for n in adjacency.get(current, []) if n not in visited]
            if not nexts:
                break
            current = nexts[0]
            chain.append(current)
            visited.add(current)
        return chain

    # ------------------------------------------------------------------
    # Productivity Insights (natural language, computed from real sessions)
    # ------------------------------------------------------------------
    def productivity_insights(self, user_id: int = 1) -> List[str]:
        sessions = self.memory.get_recent_focus_sessions(user_id=user_id, limit=30)
        if not sessions:
            return ["Log a few study sessions and FlowMind will start surfacing patterns here."]

        insights: List[str] = []

        morning = [s for s in sessions if s.start_time and s.start_time.hour < 13]
        afternoon = [s for s in sessions if s.start_time and s.start_time.hour >= 13]
        if morning and afternoon:
            avg_morning = sum(s.focus_score for s in morning) / len(morning)
            avg_afternoon = sum(s.focus_score for s in afternoon) / len(afternoon)
            if avg_afternoon > 0 and avg_morning > avg_afternoon:
                ratio = round(avg_morning / max(1.0, avg_afternoon), 1)
                insights.append(f"You are roughly {ratio}x more productive before 1 PM than after.")
            elif avg_morning > 0 and avg_afternoon > avg_morning:
                ratio = round(avg_afternoon / max(1.0, avg_morning), 1)
                insights.append(f"You are roughly {ratio}x more productive after 1 PM than before.")

        best = max(sessions, key=lambda s: s.focus_score)
        if best.start_time:
            insights.append(
                f"Your sharpest recorded session hit {int(best.focus_score)}/100 focus, starting around "
                f"{best.start_time.strftime('%I:%M %p').lstrip('0')}."
            )

        weekend = [s for s in sessions if s.start_time and s.start_time.weekday() >= 5]
        weekday = [s for s in sessions if s.start_time and s.start_time.weekday() < 5]
        if weekend and weekday:
            avg_weekend_dur = sum(s.duration_mins for s in weekend) / len(weekend)
            avg_weekday_dur = sum(s.duration_mins for s in weekday) / len(weekday)
            if avg_weekend_dur > avg_weekday_dur * 1.15:
                insights.append("Your sessions tend to run longer on weekends than on weekdays.")

        high_tab_switch = [s for s in sessions if s.tab_switch_count and s.tab_switch_count > 15]
        if len(high_tab_switch) >= max(1, len(sessions) // 3):
            insights.append(
                "Frequent tab switching shows up in a third or more of your sessions \u2014 "
                "it's your most common focus drain."
            )

        triggers = [s.distraction_triggers for s in sessions if s.distraction_triggers and s.distraction_triggers != "None"]
        if triggers:
            most_common = max(set(triggers), key=triggers.count)
            insights.append(f"Your most frequent distraction trigger recently: {most_common}.")

        if not insights:
            insights.append("Your focus patterns look stable \u2014 keep logging sessions for deeper trends.")

        return insights[:4]
