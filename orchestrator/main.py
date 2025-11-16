"""
FortFail Orchestrator - PoC Implementation

This FastAPI application serves as the central orchestrator for the FortFail
backup and restore system. It manages:
- Agent authentication and registration
- Snapshot metadata and object storage
- Restore job orchestration
- Real-time event streaming via WebSocket
- Write-Ahead Log (WAL) for audit trail
"""

import os
import json
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
import threading

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
import boto3
from botocore.client import Config
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Import WebSocket manager
from ws import router as ws_router, ws_manager

# Configuration from environment
ORCH_JWT_SECRET = os.getenv("ORCH_JWT_SECRET", "dev-jwt-secret-change-in-production")
ORCH_REG_SECRET = os.getenv("ORCH_REG_SECRET", "dev-reg-secret-change-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./orchestrator.db")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_BUCKET = os.getenv("S3_BUCKET", "fortfail-snapshots")
WAL_PATH = os.getenv("WAL_PATH", "/data/orchestrator_wal.log")

# Ensure WAL directory exists
Path(WAL_PATH).parent.mkdir(parents=True, exist_ok=True)

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# S3/MinIO client
s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

# Security
security = HTTPBearer()

# Models
class Snapshot(Base):
    """Snapshot metadata table"""
    __tablename__ = "snapshots"
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, nullable=False, index=True)
    checksum = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(Text)  # JSON blob


class RestoreJob(Base):
    """Restore job table"""
    __tablename__ = "restore_jobs"
    
    id = Column(String, primary_key=True)
    snapshot_id = Column(String, nullable=False)
    target_agent_id = Column(String, nullable=False, index=True)
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    logs = Column(Text, default="[]")  # JSON array of events


class Command(Base):
    """Command queue table"""
    __tablename__ = "commands"
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, nullable=False, index=True)
    job_id = Column(String, nullable=False)
    command_type = Column(String, nullable=False)  # restore, etc.
    payload = Column(Text, nullable=False)  # JSON blob
    status = Column(String, default="pending")  # pending, sent, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)

# Ensure S3 bucket exists
try:
    s3_client.head_bucket(Bucket=S3_BUCKET)
except:
    try:
        s3_client.create_bucket(Bucket=S3_BUCKET)
    except Exception as e:
        print(f"Warning: Could not create S3 bucket: {e}")

# Pydantic models for API
class TokenRequest(BaseModel):
    registration_secret: str
    agent_id: Optional[str] = None


class TokenResponse(BaseModel):
    token: str
    expires_in: int


class SnapshotMetadata(BaseModel):
    id: str
    agent_id: str
    checksum: str
    size: int
    metadata: Optional[Dict[str, Any]] = None


class SnapshotResponse(BaseModel):
    id: str
    presigned_url: Optional[str] = None
    upload_url: Optional[str] = None


class RestoreJobRequest(BaseModel):
    snapshot_id: str
    target_agent_id: str


class RestoreJobResponse(BaseModel):
    id: str
    snapshot_id: str
    target_agent_id: str
    status: str


class AgentInfo(BaseModel):
    id: str
    last_seen: Optional[str] = None


class CommandResponse(BaseModel):
    id: str
    command_type: str
    payload: Dict[str, Any]


class EventRequest(BaseModel):
    job_id: Optional[str] = None
    snapshot_id: Optional[str] = None
    event_type: str
    message: str
    metadata: Optional[Dict[str, Any]] = None


# FastAPI app
app = FastAPI(
    title="FortFail Orchestrator",
    description="Central orchestrator for FortFail backup and restore system",
    version="0.1.0-poc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WebSocket router
app.include_router(ws_router)

# Mount static UI if present
ui_path = Path(__file__).parent / "ui"
if ui_path.exists():
    app.mount("/control", StaticFiles(directory=str(ui_path), html=True), name="control")


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# WAL helpers
wal_lock = threading.Lock()

def append_wal(record: Dict[str, Any]):
    """Append record to WAL and broadcast to WebSocket clients"""
    record["timestamp"] = datetime.utcnow().isoformat()
    
    # Write to WAL
    with wal_lock:
        try:
            with open(WAL_PATH, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            print(f"Error writing to WAL: {e}")
    
    # Broadcast to WebSocket clients
    try:
        asyncio.create_task(ws_manager.broadcast(record))
    except RuntimeError:
        # If no event loop, use thread
        def broadcast_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(ws_manager.broadcast(record))
            loop.close()
        
        threading.Thread(target=broadcast_in_thread, daemon=True).start()


# JWT helpers
def create_token(agent_id: Optional[str] = None) -> str:
    """Create JWT token"""
    payload = {
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow(),
    }
    if agent_id:
        payload["agent_id"] = agent_id
    
    return jwt.encode(payload, ORCH_JWT_SECRET, algorithm="HS256")


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, ORCH_JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Endpoints
@app.post("/auth/token", response_model=TokenResponse)
async def mint_token(request: TokenRequest):
    """Mint JWT token using registration secret"""
    if request.registration_secret != ORCH_REG_SECRET:
        raise HTTPException(status_code=403, detail="Invalid registration secret")
    
    token = create_token(agent_id=request.agent_id)
    
    append_wal({
        "event": "token_minted",
        "agent_id": request.agent_id
    })
    
    return TokenResponse(token=token, expires_in=7 * 24 * 3600)


@app.post("/snapshots", response_model=SnapshotResponse)
async def create_snapshot(
    metadata: SnapshotMetadata,
    payload: Dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create snapshot metadata and return presigned PUT URL"""
    
    # Store metadata
    snapshot = Snapshot(
        id=metadata.id,
        agent_id=metadata.agent_id,
        checksum=metadata.checksum,
        size=metadata.size,
        metadata=json.dumps(metadata.metadata) if metadata.metadata else "{}"
    )
    db.add(snapshot)
    db.commit()
    
    # Generate presigned URL for upload
    try:
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': S3_BUCKET, 'Key': metadata.id},
            ExpiresIn=3600
        )
    except Exception as e:
        print(f"Warning: Could not generate presigned URL: {e}")
        presigned_url = None
    
    # Fallback upload URL
    upload_url = f"/snapshots/{metadata.id}/object"
    
    append_wal({
        "event": "snapshot_created",
        "snapshot_id": metadata.id,
        "agent_id": metadata.agent_id
    })
    
    return SnapshotResponse(
        id=metadata.id,
        presigned_url=presigned_url,
        upload_url=upload_url
    )


@app.post("/snapshots/{snapshot_id}/object")
async def upload_snapshot_object(
    snapshot_id: str,
    file: UploadFile = File(...),
    payload: Dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Accept multipart upload and validate SHA256 checksum"""
    
    # Get snapshot metadata
    snapshot = db.query(Snapshot).filter(Snapshot.id == snapshot_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    # Read file and compute checksum
    content = await file.read()
    computed_checksum = hashlib.sha256(content).hexdigest()
    
    if computed_checksum != snapshot.checksum:
        raise HTTPException(
            status_code=400,
            detail=f"Checksum mismatch: expected {snapshot.checksum}, got {computed_checksum}"
        )
    
    # Upload to S3/MinIO
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=snapshot_id,
            Body=content
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")
    
    append_wal({
        "event": "snapshot_uploaded",
        "snapshot_id": snapshot_id,
        "size": len(content)
    })
    
    return {"status": "uploaded", "snapshot_id": snapshot_id}


@app.get("/snapshots/{snapshot_id}/object")
async def download_snapshot_object(
    snapshot_id: str,
    payload: Dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Stream object from S3/MinIO"""
    from fastapi.responses import StreamingResponse
    
    # Verify snapshot exists
    snapshot = db.query(Snapshot).filter(Snapshot.id == snapshot_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    # Stream from S3
    try:
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=snapshot_id)
        return StreamingResponse(
            obj['Body'],
            media_type='application/octet-stream',
            headers={
                'Content-Disposition': f'attachment; filename="{snapshot_id}.tar"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download from S3: {str(e)}")


@app.post("/restore-jobs", response_model=RestoreJobResponse)
async def create_restore_job(
    request: RestoreJobRequest,
    payload: Dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create restore job and fan-out commands"""
    
    # Verify snapshot exists
    snapshot = db.query(Snapshot).filter(Snapshot.id == request.snapshot_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    # Create restore job
    job_id = f"job-{datetime.utcnow().timestamp()}"
    job = RestoreJob(
        id=job_id,
        snapshot_id=request.snapshot_id,
        target_agent_id=request.target_agent_id,
        status="pending"
    )
    db.add(job)
    
    # Create command for agent
    cmd_id = f"cmd-{datetime.utcnow().timestamp()}"
    command = Command(
        id=cmd_id,
        agent_id=request.target_agent_id,
        job_id=job_id,
        command_type="restore",
        payload=json.dumps({
            "snapshot_id": request.snapshot_id,
            "job_id": job_id
        })
    )
    db.add(command)
    db.commit()
    
    append_wal({
        "event": "restore_job_created",
        "job_id": job_id,
        "snapshot_id": request.snapshot_id,
        "target_agent_id": request.target_agent_id
    })
    
    return RestoreJobResponse(
        id=job_id,
        snapshot_id=request.snapshot_id,
        target_agent_id=request.target_agent_id,
        status="pending"
    )


@app.get("/restore-jobs/{job_id}", response_model=RestoreJobResponse)
async def get_restore_job(
    job_id: str,
    payload: Dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get restore job status"""
    job = db.query(RestoreJob).filter(RestoreJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return RestoreJobResponse(
        id=job.id,
        snapshot_id=job.snapshot_id,
        target_agent_id=job.target_agent_id,
        status=job.status
    )


@app.get("/agents", response_model=List[AgentInfo])
async def list_agents(
    payload: Dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Return deduplicated agent list from snapshots and restore jobs"""
    
    # Get unique agent IDs from snapshots
    snapshot_agents = db.query(Snapshot.agent_id).distinct().all()
    job_agents = db.query(RestoreJob.target_agent_id).distinct().all()
    
    agent_ids = set()
    for (agent_id,) in snapshot_agents:
        agent_ids.add(agent_id)
    for (agent_id,) in job_agents:
        agent_ids.add(agent_id)
    
    return [AgentInfo(id=agent_id) for agent_id in sorted(agent_ids)]


@app.get("/agent/{agent_id}/commands", response_model=List[CommandResponse])
async def get_agent_commands(
    agent_id: str,
    payload: Dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Return pending commands for agent and mark as sent"""
    
    commands = db.query(Command).filter(
        Command.agent_id == agent_id,
        Command.status == "pending"
    ).all()
    
    # Mark as sent
    for cmd in commands:
        cmd.status = "sent"
    db.commit()
    
    result = []
    for cmd in commands:
        result.append(CommandResponse(
            id=cmd.id,
            command_type=cmd.command_type,
            payload=json.loads(cmd.payload)
        ))
    
    return result


@app.post("/agent/{agent_id}/events")
async def post_agent_event(
    agent_id: str,
    event: EventRequest,
    payload: Dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Persist event and broadcast via WebSocket"""
    
    # If job_id is present, append to RestoreJob logs
    if event.job_id:
        job = db.query(RestoreJob).filter(RestoreJob.id == event.job_id).first()
        if job:
            logs = json.loads(job.logs or "[]")
            logs.append({
                "timestamp": datetime.utcnow().isoformat(),
                "agent_id": agent_id,
                "event_type": event.event_type,
                "message": event.message,
                "metadata": event.metadata
            })
            job.logs = json.dumps(logs)
            job.updated_at = datetime.utcnow()
            
            # Update job status based on event
            if event.event_type in ["restore_completed", "restore_success"]:
                job.status = "completed"
            elif event.event_type in ["restore_failed", "error"]:
                job.status = "failed"
            elif event.event_type in ["restore_started", "restore_in_progress"]:
                job.status = "in_progress"
            
            db.commit()
    
    # Append to WAL and broadcast
    append_wal({
        "event": "agent_event",
        "agent_id": agent_id,
        "job_id": event.job_id,
        "snapshot_id": event.snapshot_id,
        "event_type": event.event_type,
        "message": event.message,
        "metadata": event.metadata
    })
    
    return {"status": "ok"}


@app.get("/health/live")
async def health_live():
    """Liveness probe"""
    return {"status": "ok"}


@app.get("/health/ready")
async def health_ready(db: Session = Depends(get_db)):
    """Readiness probe - check database connectivity"""
    try:
        # Simple query to verify DB connection
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database not ready: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "FortFail Orchestrator",
        "version": "0.1.0-poc",
        "docs": "/docs",
        "control_ui": "/control",
        "websocket": "/ws"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
