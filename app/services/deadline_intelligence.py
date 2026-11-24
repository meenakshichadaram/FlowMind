import math
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.memory.memory_manager import MemoryManager
from app.schemas.pydantic_models import DeadlinePredictionResponse, DeadlineTaskSchema
from app.config.llm_factory import LLMFactory
from app.utils.logger import logger

class DeadlineIntelligenceEngine:
    """MODULE 2: Deadline Intelligence Engine
    Predicts completion probability, generates recommended daily schedules, and flags deadline risk.
    """

    def __init__(self, db_session: Session):
        self.memory = MemoryManager(db_session)
        self.llm = LLMFactory.get_llm(temperature=0.2)

    def evaluate_task_risk(self, task_id: int) -> DeadlinePredictionResponse:
        tasks = self.memory.get_deadline_tasks(user_id=1)
        target = next((t for t in tasks if t.id == task_id), None)
        
        if not target and tasks:
            target = tasks[0]

        if not target:
            # Fallback dummy prediction if no tasks exist
            return DeadlinePredictionResponse(
                task_title="Sample Assignment",
                completion_probability=0.85,
                predicted_finish_date=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                risk_score=15.0,
                risk_level="Low Risk",
                recommended_schedule=[],
                explanation="No pending deadlines found."
            )

        now = datetime.utcnow()
        days_left = max(0.5, (target.due_date - now).total_seconds() / 86400.0)
        
        # Velocity multiplier based on historical completion rate
        user = self.memory.get_user_profile(user_id=1)
        daily_capacity = user.daily_goal_hours if user else 4.0
        
        effective_hours_needed = target.estimated_hours_remaining * (1.0 + (target.complexity_level - 3) * 0.12)
        total_available = days_left * daily_capacity * target.historical_completion_rate

        margin = total_available - effective_hours_needed
        # Sigmoid probability
        prob = 1.0 / (1.0 + math.exp(-0.5 * margin))
        prob = round(max(0.05, min(0.99, prob)), 2)

        risk_score = round((1.0 - prob) * 100, 1)

        if risk_score > 70:
            level = "Critical Risk"
            status = "High Risk"
        elif risk_score > 40:
            level = "Moderate Risk"
            status = "In Progress"
        else:
            level = "Low Risk"
            status = "Pending"

        # Update record in DB
        target.completion_probability = prob
        target.risk_score = risk_score
        target.status = status
        self.memory.db.commit()

        # Build recommended schedule
        hours_per_day = round(effective_hours_needed / max(1, math.ceil(days_left)), 1)
        schedule = []
        for i in range(math.ceil(days_left)):
            day = now + timedelta(days=i)
            schedule.append({
                "date": day.strftime("%Y-%m-%d"),
                "day": day.strftime("%A"),
                "recommended_hours": min(daily_capacity, hours_per_day),
                "focus_topic": f"Work on {target.title} - Session {i+1}"
            })

        predicted_finish = (now + timedelta(days=math.ceil(effective_hours_needed / daily_capacity))).strftime("%Y-%m-%d")

        # LLM reasoning explanation
        prompt = (
            f"As FlowMind Deadline Engine, analyze deadline task '{target.title}':\n"
            f"• Due: {target.due_date.strftime('%Y-%m-%d')} ({round(days_left, 1)} days left)\n"
            f"• Est. Remaining: {target.estimated_hours_remaining} hrs (Complexity {target.complexity_level}/5)\n"
            f"• Calculated Completion Probability: {int(prob*100)}%, Risk Score: {risk_score}/100 ({level}).\n\n"
            f"Write a 2-sentence actionable warning or reassurance to the student."
        )
        explanation = self.llm.invoke(prompt).content

        return DeadlinePredictionResponse(
            task_title=target.title,
            completion_probability=prob,
            predicted_finish_date=predicted_finish,
            risk_score=risk_score,
            risk_level=level,
            recommended_schedule=schedule,
            explanation=str(explanation)
        )

    def get_all_deadlines(self, user_id: int = 1) -> List[DeadlineTaskSchema]:
        tasks = self.memory.get_deadline_tasks(user_id=user_id)
        return [DeadlineTaskSchema.model_validate(t) for t in tasks]
