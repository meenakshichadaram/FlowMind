from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database.models import (
    UserProfile, LearningGoal, Project, UnfinishedActivity,
    DeadlineTask, FocusSession, ConceptLink
)
from app.schemas.pydantic_models import (
    UnfinishedActivitySchema, DeadlineTaskSchema, FocusSessionSchema
)
from app.utils.logger import logger

class MemoryManager:
    """Handles structured long-term memory retrieval and state updates in SQLite."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_user_profile(self, user_id: int = 1) -> Optional[UserProfile]:
        return self.db.query(UserProfile).filter(UserProfile.id == user_id).first()

    # --- Unfinished Activities ---
    def get_unfinished_activities(self, user_id: int = 1, limit: int = 10) -> List[UnfinishedActivity]:
        return (
            self.db.query(UnfinishedActivity)
            .filter(UnfinishedActivity.user_id == user_id)
            .order_by(UnfinishedActivity.priority_score.desc())
            .limit(limit)
            .all()
        )

    def add_or_update_unfinished_activity(self, activity: UnfinishedActivitySchema) -> UnfinishedActivity:
        existing = None
        if activity.id:
            existing = self.db.query(UnfinishedActivity).filter(UnfinishedActivity.id == activity.id).first()

        if not existing:
            existing = self.db.query(UnfinishedActivity).filter(
                UnfinishedActivity.user_id == activity.user_id,
                UnfinishedActivity.title == activity.title
            ).first()

        if existing:
            existing.progress_percent = activity.progress_percent
            existing.priority_score = activity.priority_score
            existing.revisit_count += 1
            existing.last_accessed = datetime.utcnow()
            if activity.importance_reason:
                existing.importance_reason = activity.importance_reason
            if activity.recommended_action:
                existing.recommended_action = activity.recommended_action
            obj = existing
        else:
            obj = UnfinishedActivity(
                user_id=activity.user_id,
                title=activity.title,
                source_type=activity.source_type,
                url_or_path=activity.url_or_path,
                progress_percent=activity.progress_percent,
                priority_score=activity.priority_score,
                revisit_count=1,
                importance_reason=activity.importance_reason,
                recommended_action=activity.recommended_action,
                last_accessed=datetime.utcnow()
            )
            self.db.add(obj)

        self.db.commit()
        self.db.refresh(obj)
        return obj

    # --- Deadlines ---
    def get_deadline_tasks(self, user_id: int = 1) -> List[DeadlineTask]:
        return (
            self.db.query(DeadlineTask)
            .filter(DeadlineTask.user_id == user_id)
            .order_by(DeadlineTask.due_date.asc())
            .all()
        )

    def add_or_update_deadline(self, task: DeadlineTaskSchema) -> DeadlineTask:
        existing = None
        if task.id:
            existing = self.db.query(DeadlineTask).filter(DeadlineTask.id == task.id).first()
        
        if not existing:
            existing = self.db.query(DeadlineTask).filter(
                DeadlineTask.user_id == task.user_id,
                DeadlineTask.title == task.title
            ).first()

        if existing:
            existing.due_date = task.due_date
            existing.estimated_hours_remaining = task.estimated_hours_remaining
            existing.complexity_level = task.complexity_level
            existing.historical_completion_rate = task.historical_completion_rate
            existing.completion_probability = task.completion_probability
            existing.risk_score = task.risk_score
            existing.status = task.status
            obj = existing
        else:
            obj = DeadlineTask(
                user_id=task.user_id,
                title=task.title,
                course_or_project=task.course_or_project,
                due_date=task.due_date,
                estimated_hours_remaining=task.estimated_hours_remaining,
                complexity_level=task.complexity_level,
                historical_completion_rate=task.historical_completion_rate,
                completion_probability=task.completion_probability,
                risk_score=task.risk_score,
                status=task.status
            )
            self.db.add(obj)

        self.db.commit()
        self.db.refresh(obj)
        return obj

    # --- Focus Sessions ---
    def get_recent_focus_sessions(self, user_id: int = 1, limit: int = 5) -> List[FocusSession]:
        return (
            self.db.query(FocusSession)
            .filter(FocusSession.user_id == user_id)
            .order_by(FocusSession.start_time.desc())
            .limit(limit)
            .all()
        )

    def record_focus_session(self, session_data: FocusSessionSchema) -> FocusSession:
        obj = FocusSession(
            user_id=session_data.user_id,
            start_time=session_data.start_time or datetime.utcnow(),
            end_time=session_data.end_time or (datetime.utcnow() + timedelta(minutes=session_data.duration_mins)),
            duration_mins=session_data.duration_mins,
            distraction_count=session_data.distraction_count,
            tab_switch_count=session_data.tab_switch_count,
            focus_score=session_data.focus_score,
            distraction_triggers=session_data.distraction_triggers
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    # --- Concept Links ---
    def get_concept_links(self) -> List[ConceptLink]:
        return self.db.query(ConceptLink).all()

    def add_concept_link(self, source: str, target: str, rel_type: str = "relates_to", strength: float = 1.0, ref: str = "") -> ConceptLink:
        obj = ConceptLink(
            source_concept=source,
            target_concept=target,
            relationship_type=rel_type,
            strength=strength,
            resource_ref=ref
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    # --- Full Memory Snapshot ---
    def get_full_student_memory_snapshot(self, user_id: int = 1) -> Dict[str, Any]:
        user = self.get_user_profile(user_id)
        unfinished = self.get_unfinished_activities(user_id)
        deadlines = self.get_deadline_tasks(user_id)
        focus = self.get_recent_focus_sessions(user_id)
        
        return {
            "user_name": user.name if user else "Student",
            "daily_goal_hours": user.daily_goal_hours if user else 4.0,
            "unfinished_count": len(unfinished),
            "top_unfinished": [u.title for u in unfinished[:3]],
            "pending_deadlines_count": len(deadlines),
            "high_risk_deadlines": [d.title for d in deadlines if d.risk_score > 60],
            "recent_focus_avg": sum(f.focus_score for f in focus) / len(focus) if focus else 80.0
        }
