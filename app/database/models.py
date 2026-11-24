from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    preferred_work_hours = Column(String(100), default="09:00 - 17:00")
    avg_study_session_mins = Column(Integer, default=45)
    daily_goal_hours = Column(Float, default=4.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    goals = relationship("LearningGoal", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    unfinished_activities = relationship("UnfinishedActivity", back_populates="user", cascade="all, delete-orphan")
    deadlines = relationship("DeadlineTask", back_populates="user", cascade="all, delete-orphan")
    focus_sessions = relationship("FocusSession", back_populates="user", cascade="all, delete-orphan")


class LearningGoal(Base):
    __tablename__ = "learning_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    title = Column(String(200), nullable=False)
    category = Column(String(100), default="General")
    target_date = Column(String(50), nullable=True)
    status = Column(String(50), default="Active")  # Active, Completed, Paused

    user = relationship("UserProfile", back_populates="goals")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    name = Column(String(200), nullable=False)
    tech_stack = Column(String(200), default="Python, FastAPI")
    completion_percentage = Column(Float, default=0.0)
    last_active_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProfile", back_populates="projects")


class UnfinishedActivity(Base):
    __tablename__ = "unfinished_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    title = Column(String(250), nullable=False)
    source_type = Column(String(50), nullable=False)  # PDF, Video, Article, App, Code, Note
    url_or_path = Column(Text, nullable=True)
    progress_percent = Column(Float, default=0.0)
    priority_score = Column(Float, default=50.0)  # 0 to 100
    revisit_count = Column(Integer, default=0)
    importance_reason = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProfile", back_populates="unfinished_activities")


class DeadlineTask(Base):
    __tablename__ = "deadline_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    title = Column(String(250), nullable=False)
    course_or_project = Column(String(150), nullable=False)
    due_date = Column(DateTime, nullable=False)
    estimated_hours_remaining = Column(Float, nullable=False)
    complexity_level = Column(Integer, default=3)  # 1 to 5
    historical_completion_rate = Column(Float, default=0.85)
    completion_probability = Column(Float, default=0.75)
    risk_score = Column(Float, default=25.0)  # 0 to 100
    status = Column(String(50), default="Pending")  # Pending, In Progress, Completed, High Risk

    user = relationship("UserProfile", back_populates="deadlines")


class FocusSession(Base):
    __tablename__ = "focus_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_mins = Column(Integer, default=0)
    distraction_count = Column(Integer, default=0)
    tab_switch_count = Column(Integer, default=0)
    focus_score = Column(Float, default=85.0)  # 0 to 100
    distraction_triggers = Column(Text, default="Social Media, Tab Switching")

    user = relationship("UserProfile", back_populates="focus_sessions")


class ConceptLink(Base):
    __tablename__ = "concept_links"

    id = Column(Integer, primary_key=True, index=True)
    source_concept = Column(String(150), nullable=False)
    target_concept = Column(String(150), nullable=False)
    relationship_type = Column(String(100), default="prerequisite")  # prerequisite, relates_to, builds_on
    strength = Column(Float, default=1.0)
    resource_ref = Column(Text, nullable=True)
