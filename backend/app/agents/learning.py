"""Agent Learning System with ML pipeline integration."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from app.core import get_settings


settings = get_settings()


class FeedbackType(str, Enum):
    """Types of feedback for learning."""
    HUMAN_CORRECTION = "human_correction"
    OUTCOME_RESULT = "outcome_result"
    PERFORMANCE_METRIC = "performance_metric"
    USER_RATING = "user_rating"


class TrainingJobStatus(str, Enum):
    """Training job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Feedback:
    """Feedback data for agent learning."""
    
    def __init__(
        self,
        feedback_id: str,
        task_id: str,
        agent_id: str,
        feedback_type: FeedbackType,
        content: dict,
        source_user_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        self.feedback_id = feedback_id
        self.task_id = task_id
        self.agent_id = agent_id
        self.feedback_type = feedback_type
        self.content = content
        self.source_user_id = source_user_id
        self.timestamp = timestamp or datetime.now(timezone.utc)
    
    def to_dict(self) -> dict:
        return {
            "feedback_id": self.feedback_id,
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "feedback_type": self.feedback_type.value,
            "content": self.content,
            "source_user_id": self.source_user_id,
            "timestamp": self.timestamp.isoformat()
        }


class ModelMetadata:
    """Metadata for trained models in the registry."""
    
    def __init__(
        self,
        model_id: str,
        model_name: str,
        version: str,
        agent_id: str,
        training_job_id: str,
        metrics: dict,
        artifact_path: Optional[str] = None,
        is_active: bool = False,
        created_at: Optional[datetime] = None
    ):
        self.model_id = model_id
        self.model_name = model_name
        self.version = version
        self.agent_id = agent_id
        self.training_job_id = training_job_id
        self.metrics = metrics
        self.artifact_path = artifact_path
        self.is_active = is_active
        self.created_at = created_at or datetime.now(timezone.utc)
    
    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "version": self.version,
            "agent_id": self.agent_id,
            "training_job_id": self.training_job_id,
            "metrics": self.metrics,
            "artifact_path": self.artifact_path,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }


class TrainingJob:
    """Training job definition."""
    
    def __init__(
        self,
        job_id: str,
        agent_id: str,
        model_name: str,
        training_config: dict,
        status: TrainingJobStatus = TrainingJobStatus.PENDING,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        result_model_id: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        self.job_id = job_id
        self.agent_id = agent_id
        self.model_name = model_name
        self.training_config = training_config
        self.status = status
        self.started_at = started_at
        self.completed_at = completed_at
        self.result_model_id = result_model_id
        self.error_message = error_message
        self.created_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "agent_id": self.agent_id,
            "model_name": self.model_name,
            "training_config": self.training_config,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result_model_id": self.result_model_id,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat()
        }


class AgentLearningSystem:
    """
    Learning system for continuous agent improvement.
    
    Features:
    - Collect feedback from human oversight and outcomes
    - Trigger training jobs via Celery
    - Track model versions in registry
    - Fetch latest model for inference
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.feedback_buffer: List[Feedback] = []
        self.training_jobs: Dict[str, TrainingJob] = {}
        self.model_registry: Dict[str, ModelMetadata] = {}
    
    def collect_feedback(
        self,
        task_id: str,
        feedback_type: FeedbackType,
        content: dict,
        source_user_id: Optional[str] = None
    ) -> Feedback:
        """
        Collect feedback for learning.
        
        This triggers model training when feedback buffer reaches threshold.
        """
        feedback = Feedback(
            feedback_id=str(uuid.uuid4()),
            task_id=task_id,
            agent_id=self.agent_id,
            feedback_type=feedback_type,
            content=content,
            source_user_id=source_user_id
        )
        
        self.feedback_buffer.append(feedback)
        
        # Check if we should trigger training
        if self._should_trigger_training():
            self._enqueue_training_job()
        
        return feedback
    
    def _should_trigger_training(self, threshold: int = 100) -> bool:
        """Check if training should be triggered based on feedback count."""
        return len(self.feedback_buffer) >= threshold
    
    def _enqueue_training_job(self) -> Optional[TrainingJob]:
        """
        Enqueue a training job via Celery.
        
        This is a placeholder - actual implementation would use Celery tasks.
        """
        job = TrainingJob(
            job_id=str(uuid.uuid4()),
            agent_id=self.agent_id,
            model_name=f"agent_{self.agent_id}_model",
            training_config={
                "feedback_count": len(self.feedback_buffer),
                "epochs": 10,
                "batch_size": 32,
                "learning_rate": 0.001
            }
        )
        
        self.training_jobs[job.job_id] = job
        
        # In real implementation, this would call Celery task
        # from app.tasks.training import run_training_job
        # run_training_job.delay(job.job_id, [f.to_dict() for f in self.feedback_buffer])
        
        # Clear feedback buffer after enqueuing
        self.feedback_buffer = []
        
        return job
    
    def enqueue_training_job_manual(
        self,
        model_name: str,
        training_config: dict,
        feedback_ids: Optional[List[str]] = None
    ) -> TrainingJob:
        """Manually enqueue a training job with custom configuration."""
        job = TrainingJob(
            job_id=str(uuid.uuid4()),
            agent_id=self.agent_id,
            model_name=model_name,
            training_config={
                **training_config,
                "feedback_ids": feedback_ids or []
            }
        )
        
        self.training_jobs[job.job_id] = job
        
        # Placeholder for Celery task
        return job
    
    def update_training_job_status(
        self,
        job_id: str,
        status: TrainingJobStatus,
        result_model_id: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Optional[TrainingJob]:
        """Update status of a training job."""
        if job_id not in self.training_jobs:
            return None
        
        job = self.training_jobs[job_id]
        job.status = status
        
        if status == TrainingJobStatus.RUNNING:
            job.started_at = datetime.now(timezone.utc)
        elif status in [TrainingJobStatus.COMPLETED, TrainingJobStatus.FAILED]:
            job.completed_at = datetime.now(timezone.utc)
            job.result_model_id = result_model_id
            job.error_message = error_message
        
        return job
    
    def register_model(
        self,
        model_name: str,
        version: str,
        training_job_id: str,
        metrics: dict,
        artifact_path: Optional[str] = None,
        activate: bool = False
    ) -> ModelMetadata:
        """Register a trained model in the registry."""
        model = ModelMetadata(
            model_id=str(uuid.uuid4()),
            model_name=model_name,
            version=version,
            agent_id=self.agent_id,
            training_job_id=training_job_id,
            metrics=metrics,
            artifact_path=artifact_path,
            is_active=activate
        )
        
        self.model_registry[model.model_id] = model
        
        # Deactivate other versions if activating this one
        if activate:
            for m in self.model_registry.values():
                if m.model_name == model_name and m.model_id != model.model_id:
                    m.is_active = False
        
        return model
    
    def get_active_model(self, model_name: str) -> Optional[ModelMetadata]:
        """Get the currently active model for inference."""
        for model in self.model_registry.values():
            if model.model_name == model_name and model.is_active:
                return model
        return None
    
    def get_latest_model(self, model_name: str) -> Optional[ModelMetadata]:
        """Get the latest model version by creation time."""
        models = [
            m for m in self.model_registry.values()
            if m.model_name == model_name
        ]
        if not models:
            return None
        return max(models, key=lambda m: m.created_at)
    
    def activate_model(self, model_id: str) -> bool:
        """Activate a specific model version."""
        if model_id not in self.model_registry:
            return False
        
        model = self.model_registry[model_id]
        
        # Deactivate other versions
        for m in self.model_registry.values():
            if m.model_name == model.model_name:
                m.is_active = False
        
        model.is_active = True
        return True
    
    def get_training_jobs(
        self,
        status: Optional[TrainingJobStatus] = None
    ) -> List[TrainingJob]:
        """Get training jobs, optionally filtered by status."""
        jobs = list(self.training_jobs.values())
        if status:
            jobs = [j for j in jobs if j.status == status]
        return sorted(jobs, key=lambda j: j.created_at, reverse=True)
    
    def get_feedback_summary(self) -> dict:
        """Get summary of collected feedback."""
        by_type = {}
        for f in self.feedback_buffer:
            t = f.feedback_type.value
            by_type[t] = by_type.get(t, 0) + 1
        
        return {
            "total_pending": len(self.feedback_buffer),
            "by_type": by_type,
            "models_registered": len(self.model_registry),
            "active_training_jobs": len([
                j for j in self.training_jobs.values()
                if j.status == TrainingJobStatus.RUNNING
            ])
        }
