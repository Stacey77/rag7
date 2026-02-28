"""Learning agent module for continuous improvement and ML pipeline integration."""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import uuid

from app.db.models import AgentType
from app.db.crud import FeedbackCRUD, ModelCRUD


class AgentLearningSystem:
    """Manages agent learning and model training pipeline."""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.training_queue = []
    
    async def collect_feedback(
        self,
        db,
        task_id: int,
        user_id: str,
        feedback_type: str,
        rating: Optional[int] = None,
        feedback_text: Optional[str] = None,
        feedback_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Collect user feedback for learning."""
        # Store feedback in database
        feedback = await FeedbackCRUD.create_feedback(
            db,
            task_id=task_id,
            user_id=user_id,
            feedback_type=feedback_type,
            rating=rating,
            feedback_text=feedback_text,
            feedback_data=feedback_data
        )
        
        # Check if we should trigger training
        should_train = await self.should_trigger_training(db)
        
        result = {
            "feedback_id": feedback.id,
            "task_id": task_id,
            "stored": True,
            "training_triggered": should_train
        }
        
        if should_train:
            training_job = await self.trigger_training(db)
            result["training_job_id"] = training_job["job_id"]
        
        return result
    
    async def should_trigger_training(self, db) -> bool:
        """Determine if training should be triggered based on feedback count."""
        # Get unused feedback count
        unused_feedback = await FeedbackCRUD.get_unused_feedback(db, limit=1000)
        
        # Trigger training if we have enough new feedback
        TRAINING_THRESHOLD = 100
        return len(unused_feedback) >= TRAINING_THRESHOLD
    
    async def trigger_training(self, db) -> Dict[str, Any]:
        """Trigger a training job for the agent."""
        # Get unused feedback for training
        feedback_data = await FeedbackCRUD.get_unused_feedback(db, limit=1000)
        
        # Generate unique job ID
        job_id = f"train_{self.agent_type.value}_{uuid.uuid4().hex[:8]}"
        
        # In production, this would enqueue a Celery task or submit to a job runner
        # For now, we'll just create a placeholder training job
        training_job = {
            "job_id": job_id,
            "agent_type": self.agent_type.value,
            "feedback_count": len(feedback_data),
            "status": "queued",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Add to training queue (in production, this would be Celery/Redis)
        self.training_queue.append(training_job)
        
        return training_job
    
    async def run_training_job(
        self,
        db,
        job_id: str,
        feedback_ids: List[int]
    ) -> Dict[str, Any]:
        """Execute a training job (placeholder implementation)."""
        # This is a placeholder - in production would run actual ML training
        
        # Simulate training
        model_version = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Create model registry entry
        model = await ModelCRUD.create_model(
            db,
            name=f"{self.agent_type.value}_model",
            version=model_version,
            agent_type=self.agent_type,
            training_job_id=job_id,
            model_path=f"/models/{self.agent_type.value}/{model_version}",
            metrics={
                "accuracy": 0.92,
                "precision": 0.90,
                "recall": 0.89,
                "f1_score": 0.895,
                "training_samples": len(feedback_ids)
            }
        )
        
        return {
            "job_id": job_id,
            "model_id": model.id,
            "model_version": model_version,
            "status": "completed",
            "metrics": model.metrics
        }
    
    async def get_latest_model(self, db) -> Optional[Dict[str, Any]]:
        """Get the latest active model for this agent type."""
        model = await ModelCRUD.get_latest_model(db, self.agent_type)
        
        if model:
            return {
                "model_id": model.id,
                "name": model.name,
                "version": model.version,
                "agent_type": model.agent_type.value,
                "model_path": model.model_path,
                "metrics": model.metrics,
                "deployed_at": model.deployed_at.isoformat() if model.deployed_at else None
            }
        
        return None
    
    async def apply_model_update(
        self,
        db,
        agent_id: int,
        model_id: int
    ) -> Dict[str, Any]:
        """Apply a model update to an agent."""
        # In production, this would trigger agent reload/restart with new model
        
        return {
            "agent_id": agent_id,
            "model_id": model_id,
            "status": "applied",
            "applied_at": datetime.utcnow().isoformat()
        }


class TrainingJobRunner:
    """Background job runner for ML training tasks."""
    
    @staticmethod
    async def process_training_job(db, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a training job (placeholder for Celery task)."""
        job_id = job_data["job_id"]
        agent_type = AgentType(job_data["agent_type"])
        
        # Create learning system
        learning_system = AgentLearningSystem(agent_type)
        
        # Get feedback for training
        feedback_data = await FeedbackCRUD.get_unused_feedback(db, limit=1000)
        feedback_ids = [f.id for f in feedback_data]
        
        # Run training
        result = await learning_system.run_training_job(
            db,
            job_id,
            feedback_ids
        )
        
        return result
