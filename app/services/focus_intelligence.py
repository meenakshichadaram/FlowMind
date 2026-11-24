from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.memory.memory_manager import MemoryManager
from app.schemas.pydantic_models import FocusAnalysisResponse, FocusSessionSchema
from app.config.llm_factory import LLMFactory
from app.utils.logger import logger

class FocusIntelligenceEngine:
    """MODULE 4: Focus Intelligence Engine
    Analyzes student focus patterns, tab switches, and distraction triggers to optimize study sessions.
    """

    def __init__(self, db_session: Session):
        self.memory = MemoryManager(db_session)
        self.llm = LLMFactory.get_llm(temperature=0.2)

    def analyze_focus_patterns(self, user_id: int = 1) -> FocusAnalysisResponse:
        sessions = self.memory.get_recent_focus_sessions(user_id=user_id, limit=10)
        
        if not sessions:
            return FocusAnalysisResponse(
                current_focus_score=85.0,
                productivity_state="Normal",
                distraction_risks=["No recent focus logs found"],
                recommended_session_mins=45,
                optimal_break_mins=10,
                actionable_insights=["Start your first focus session to track real-time focus metrics."]
            )

        avg_score = sum(s.focus_score for s in sessions) / len(sessions)
        avg_distractions = sum(s.distraction_count for s in sessions) / len(sessions)
        avg_tabs = sum(s.tab_switch_count for s in sessions) / len(sessions)

        if avg_score >= 80:
            state = "Peak Flow"
            session_len = 50
            break_len = 10
        elif avg_score >= 60:
            state = "Moderate Focus"
            session_len = 40
            break_len = 8
        else:
            state = "High Distraction / Fatigue"
            session_len = 25
            break_len = 5

        # Distraction triggers
        all_triggers = [s.distraction_triggers for s in sessions if s.distraction_triggers]
        trigger_summary = ", ".join(all_triggers[:3]) if all_triggers else "Tab switching"

        # LLM insights
        prompt = (
            f"As FlowMind Focus Engine, analyze recent student focus data:\n"
            f"• Average Focus Score: {round(avg_score, 1)}/100 ({state})\n"
            f"• Avg Distractions per session: {round(avg_distractions, 1)}\n"
            f"• Avg Tab Switches per session: {round(avg_tabs, 1)}\n"
            f"• Top Triggers: {trigger_summary}\n\n"
            f"Provide 2 short, highly tailored behavioral recommendations to maintain focus."
        )
        insights_str = self.llm.invoke(prompt).content
        insights = [str(insights_str)]

        return FocusAnalysisResponse(
            current_focus_score=round(avg_score, 1),
            productivity_state=state,
            distraction_risks=[f"Frequent Tab Switching (~{int(avg_tabs)} switches/session)", f"Distraction Triggers: {trigger_summary}"],
            recommended_session_mins=session_len,
            optimal_break_mins=break_len,
            actionable_insights=insights
        )

    def log_new_focus_session(
        self,
        duration_mins: int,
        distraction_count: int,
        tab_switches: int,
        triggers: str = "Tab Switching"
    ) -> FocusSessionSchema:
        # Calculate focus score
        penalty = (distraction_count * 8.0) + (tab_switches * 1.5)
        score = max(15.0, min(100.0, 100.0 - penalty))
        
        session = FocusSessionSchema(
            user_id=1,
            start_time=datetime.utcnow() - timedelta(minutes=duration_mins),
            end_time=datetime.utcnow(),
            duration_mins=duration_mins,
            distraction_count=distraction_count,
            tab_switch_count=tab_switches,
            focus_score=round(score, 1),
            distraction_triggers=triggers
        )
        recorded = self.memory.record_focus_session(session)
        return FocusSessionSchema.model_validate(recorded)
