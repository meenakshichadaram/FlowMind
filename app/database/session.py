from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.settings import settings
from app.database.models import (
    Base, UserProfile, LearningGoal, Project, UnfinishedActivity,
    DeadlineTask, FocusSession, ConceptLink
)
from app.utils.logger import logger

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for obtaining database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Creates tables and populates seed data if empty."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized.")

    db = SessionLocal()
    try:
        # Check if seed user exists
        user = db.query(UserProfile).filter_by(email="alex.student@university.edu").first()
        if not user:
            logger.info("Seeding initial student profile and workflow state...")
            user = UserProfile(
                name="Alex Dev",
                email="alex.student@university.edu",
                preferred_work_hours="09:00 - 13:00, 15:00 - 18:00",
                avg_study_session_mins=50,
                daily_goal_hours=5.0
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Seed Learning Goals
            db.add_all([
                LearningGoal(user_id=user.id, title="Master LangGraph Orchestration", category="AI Engineering", target_date="2026-08-30", status="Active"),
                LearningGoal(user_id=user.id, title="Complete Distributed Systems Coursework", category="Computer Science", target_date="2026-09-15", status="Active"),
                LearningGoal(user_id=user.id, title="Prepare for Machine Learning Internship", category="Career", target_date="2026-08-25", status="Active"),
            ])

            # Seed Projects
            db.add_all([
                Project(user_id=user.id, name="FlowMind AI Platform", tech_stack="Python, FastAPI, LangGraph, Streamlit", completion_percentage=75.0),
                Project(user_id=user.id, name="Distributed Key-Value Store", tech_stack="Go, Raft Consensus", completion_percentage=30.0),
            ])

            # Seed Unfinished Activities
            now = datetime.utcnow()
            db.add_all([
                UnfinishedActivity(
                    user_id=user.id,
                    title="Attention Is All You Need Paper (PDF)",
                    source_type="PDF",
                    url_or_path="/uploads/attention_paper.pdf",
                    progress_percent=35.0,
                    priority_score=88.5,
                    revisit_count=4,
                    importance_reason="Core foundation paper required for upcoming Deep Learning Exam.",
                    recommended_action="Read Section 3: Multi-Head Attention Mechanism (Pages 4-6).",
                    last_accessed=now - timedelta(days=2)
                ),
                UnfinishedActivity(
                    user_id=user.id,
                    title="MIT 6.824 Distributed Systems Lecture 5",
                    source_type="Video",
                    url_or_path="https://youtube.com/watch?v=mock123",
                    progress_percent=60.0,
                    priority_score=79.0,
                    revisit_count=2,
                    importance_reason="Essential concepts for Raft RPC Implementation assignment.",
                    recommended_action="Watch remaining 25 minutes starting from 34:10.",
                    last_accessed=now - timedelta(days=1)
                ),
                UnfinishedActivity(
                    user_id=user.id,
                    title="OpenAI Cookbook - Vector Search & Hybrid RAG",
                    source_type="Article",
                    url_or_path="https://github.com/openai/openai-cookbook",
                    progress_percent=20.0,
                    priority_score=65.0,
                    revisit_count=1,
                    importance_reason="Helpful patterns for Knowledge Fusion Engine optimization.",
                    recommended_action="Revisit code snippet on reciprocal rank fusion.",
                    last_accessed=now - timedelta(days=4)
                ),
                UnfinishedActivity(
                    user_id=user.id,
                    title="Google Brain ML Internship Application",
                    source_type="App",
                    url_or_path="https://careers.google.com/jobs/mock",
                    progress_percent=80.0,
                    priority_score=92.0,
                    revisit_count=5,
                    importance_reason="High urgency deadline approaching in 3 days.",
                    recommended_action="Review cover letter draft and submit final application.",
                    last_accessed=now - timedelta(hours=8)
                )
            ])

            # Seed Deadline Tasks
            db.add_all([
                DeadlineTask(
                    user_id=user.id,
                    title="Distributed Systems Lab 2 - Raft Consensus",
                    course_or_project="CS 6824",
                    due_date=now + timedelta(days=3),
                    estimated_hours_remaining=8.5,
                    complexity_level=5,
                    historical_completion_rate=0.80,
                    completion_probability=0.62,
                    risk_score=78.0,
                    status="High Risk"
                ),
                DeadlineTask(
                    user_id=user.id,
                    title="Machine Learning Homework 4 - Transformer Decoder",
                    course_or_project="CS 4780",
                    due_date=now + timedelta(days=6),
                    estimated_hours_remaining=4.0,
                    complexity_level=3,
                    historical_completion_rate=0.90,
                    completion_probability=0.88,
                    risk_score=22.0,
                    status="In Progress"
                ),
                DeadlineTask(
                    user_id=user.id,
                    title="FlowMind AI Capstone Milestone 1",
                    course_or_project="Capstone",
                    due_date=now + timedelta(days=10),
                    estimated_hours_remaining=6.0,
                    complexity_level=4,
                    historical_completion_rate=0.95,
                    completion_probability=0.94,
                    risk_score=12.0,
                    status="Pending"
                )
            ])

            # Seed Focus Sessions
            db.add_all([
                FocusSession(
                    user_id=user.id,
                    start_time=now - timedelta(days=1, hours=4),
                    end_time=now - timedelta(days=1, hours=3),
                    duration_mins=60,
                    distraction_count=2,
                    tab_switch_count=14,
                    focus_score=82.0,
                    distraction_triggers="Reddit, Discord notifications"
                ),
                FocusSession(
                    user_id=user.id,
                    start_time=now - timedelta(hours=5),
                    end_time=now - timedelta(hours=4),
                    duration_mins=45,
                    distraction_count=5,
                    tab_switch_count=28,
                    focus_score=58.0,
                    distraction_triggers="YouTube shorts, Email checking"
                ),
                FocusSession(
                    user_id=user.id,
                    start_time=now - timedelta(hours=2),
                    end_time=now - timedelta(hours=1),
                    duration_mins=50,
                    distraction_count=1,
                    tab_switch_count=6,
                    focus_score=94.0,
                    distraction_triggers="None"
                )
            ])

            # Seed Concept Links for Knowledge Fusion Graph
            db.add_all([
                ConceptLink(source_concept="Self-Attention", target_concept="Transformer Architecture", relationship_type="builds_on", strength=0.95, resource_ref="Attention Is All You Need Paper"),
                ConceptLink(source_concept="Multi-Head Attention", target_concept="Self-Attention", relationship_type="prerequisite", strength=0.90, resource_ref="Attention Is All You Need Paper"),
                ConceptLink(source_concept="Raft Consensus", target_concept="State Machine Replication", relationship_type="prerequisite", strength=0.88, resource_ref="MIT 6.824 Lecture 5"),
                ConceptLink(source_concept="Vector Embeddings", target_concept="Semantic Search", relationship_type="relates_to", strength=0.85, resource_ref="OpenAI Cookbook"),
                ConceptLink(source_concept="ChromaDB Indexing", target_concept="Vector Embeddings", relationship_type="builds_on", strength=0.92, resource_ref="FlowMind AI Doc")
            ])

            db.commit()
            logger.info("Seed data successfully added to SQLite database.")
    except Exception as e:
        db.rollback()
        logger.error(f"Database initialization error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
