from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.memory.memory_manager import MemoryManager
from app.schemas.pydantic_models import IntentRecoveryResponse, UnfinishedActivitySchema
from app.config.llm_factory import LLMFactory
from app.utils.logger import logger

class IntentRecoveryEngine:
    """MODULE 1: Intent Recovery Engine
    Automatically detects, prioritizes, explains, and recommends next actions for unfinished digital work.
    """

    def __init__(self, db_session: Session):
        self.memory = MemoryManager(db_session)
        self.llm = LLMFactory.get_llm(temperature=0.2)

    def analyze_unfinished_work(self, user_id: int = 1) -> IntentRecoveryResponse:
        activities = self.memory.get_unfinished_activities(user_id=user_id, limit=20)
        
        # Recalculate dynamic priority scores
        scored_activities = []
        now = datetime.utcnow()
        
        for act in activities:
            days_inactive = (now - (act.last_accessed or now)).total_seconds() / 86400.0
            
            # Base priority score decay & boost
            base = act.priority_score
            decay = min(20.0, days_inactive * 2.0)
            revisit_boost = min(15.0, act.revisit_count * 3.0)
            progress_penalty = (100.0 - act.progress_percent) * 0.2
            
            dynamic_score = round(max(10.0, min(99.0, base - decay + revisit_boost + progress_penalty)), 1)
            act.priority_score = dynamic_score
            
            scored_activities.append(UnfinishedActivitySchema.model_validate(act))

        # Sort by dynamic priority
        scored_activities.sort(key=lambda x: x.priority_score, reverse=True)
        top_activities = scored_activities[:5]

        # Generate workflow summary & recommendation using LLM reasoning
        top_titles = [f"{a.title} ({a.source_type}, Progress: {a.progress_percent}%)" for a in top_activities]
        prompt = (
            f"You are FlowMind AI's Intent Recovery Engine. The student has the following top unfinished activities:\n"
            f"{'\n'.join(top_titles)}\n\n"
            f"Provide a concise summary explaining why resolving these items is critical, "
            f"and recommend the single highest-impact action the student should take right now."
        )
        llm_reply = self.llm.invoke(prompt).content

        recommended = top_activities[0].recommended_action if top_activities else "No pending unfinished items found."

        return IntentRecoveryResponse(
            unfinished_count=len(activities),
            top_priorities=top_activities,
            workflow_summary=str(llm_reply),
            recommended_next_step=str(recommended)
        )

    def register_new_unfinished_item(
        self,
        title: str,
        source_type: str,
        url_or_path: str = "",
        progress: float = 0.0,
        reason: str = "",
        action: str = ""
    ) -> UnfinishedActivitySchema:
        schema = UnfinishedActivitySchema(
            user_id=1,
            title=title,
            source_type=source_type,
            url_or_path=url_or_path,
            progress_percent=progress,
            priority_score=75.0,
            importance_reason=reason or f"Recently flagged unfinished {source_type}",
            recommended_action=action or f"Resume reviewing {title}"
        )
        saved = self.memory.add_or_update_unfinished_activity(schema)
        return UnfinishedActivitySchema.model_validate(saved)
