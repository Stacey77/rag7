"""Database models for the Agentic Agent platform."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class TaskState(str, enum.Enum):
    """Task state enumeration."""
    QUEUED = "queued"
    ASSIGNED = "assigned"
    ACKED = "acked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    FAILED = "failed"
    ESCALATED = "escalated"


class AgentType(str, enum.Enum):
    """Agent type enumeration."""
    COMMUNICATION = "communication"
    DECISION = "decision"
    DELEGATION = "delegation"
    LEARNING = "learning"


class Event(Base):
    """Event store for all system events."""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True, index=True)
    user_id = Column(String(100), nullable=True, index=True)
    
    # Relationships
    task = relationship("Task", back_populates="events")
    agent = relationship("Agent", back_populates="events")


class Task(Base):
    """Task tracking and state management."""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(100), nullable=False, index=True)
    state = Column(SQLEnum(TaskState), default=TaskState.QUEUED, nullable=False, index=True)
    priority = Column(Integer, default=0, nullable=False, index=True)
    
    # Task metadata
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Assignment and retry tracking
    assigned_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True, index=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    assigned_at = Column(DateTime, nullable=True)
    acked_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    escalated_at = Column(DateTime, nullable=True)
    
    # Timeouts
    ack_timeout_seconds = Column(Integer, default=30, nullable=False)
    task_timeout_seconds = Column(Integer, default=300, nullable=False)
    
    # Relationships
    assigned_agent = relationship("Agent", back_populates="tasks")
    events = relationship("Event", back_populates="task", cascade="all, delete-orphan")
    audits = relationship("Audit", back_populates="task", cascade="all, delete-orphan")


class Agent(Base):
    """Agent registry and metadata."""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(SQLEnum(AgentType), nullable=False, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    version = Column(String(50), nullable=False)
    
    # Agent state
    is_active = Column(Integer, default=1, nullable=False)  # 1=active, 0=inactive
    current_load = Column(Integer, default=0, nullable=False)
    max_load = Column(Integer, default=10, nullable=False)
    
    # Model reference
    current_model_id = Column(Integer, ForeignKey("models.id"), nullable=True)
    
    # Metadata
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    tasks = relationship("Task", back_populates="assigned_agent")
    events = relationship("Event", back_populates="agent")
    current_model = relationship("Model", foreign_keys=[current_model_id])


class Audit(Base):
    """Audit log for oversight and compliance."""
    __tablename__ = "audits"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    user_role = Column(String(50), nullable=False)
    
    # Context
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True, index=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(100), nullable=True)
    
    # Details
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(String(50), nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="audits")


class Feedback(Base):
    """User feedback for agent learning."""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    
    # Feedback data
    rating = Column(Integer, nullable=True)  # 1-5 scale
    feedback_type = Column(String(50), nullable=False)  # positive, negative, neutral
    feedback_text = Column(Text, nullable=True)
    feedback_data = Column(JSON, nullable=True)
    
    # Training metadata
    used_for_training = Column(Integer, default=0, nullable=False)  # 0=no, 1=yes
    training_job_id = Column(String(100), nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class Model(Base):
    """Model registry for ML models."""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    agent_type = Column(SQLEnum(AgentType), nullable=False, index=True)
    
    # Model artifacts
    model_path = Column(String(500), nullable=True)
    model_url = Column(String(500), nullable=True)
    metrics = Column(JSON, nullable=True)
    
    # Training metadata
    training_job_id = Column(String(100), nullable=True, unique=True)
    trained_on_feedback_count = Column(Integer, default=0, nullable=False)
    training_started_at = Column(DateTime, nullable=True)
    training_completed_at = Column(DateTime, nullable=True)
    
    # Deployment
    is_active = Column(Integer, default=0, nullable=False)  # 0=inactive, 1=active
    deployed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
