"""
FortFail Agent - PoC Implementation

This agent handles:
- JWT bootstrap and authentication
- Snapshot creation and upload
- Command polling and execution
- Restore operations
- Event reporting to orchestrator
"""

import os
import time
import hashlib
import tarfile
import tempfile
import json
from pathlib import Path
from typing import Optional, Dict, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8000")
AGENT_ID = os.getenv("AGENT_ID", f"agent-{os.getpid()}")
AGENT_REG_SECRET = os.getenv("AGENT_REG_SECRET", "dev-reg-secret-change-in-production")
ORCH_JWT = os.getenv("ORCH_JWT")  # Optional pre-provisioned JWT
BACKUP_DIR = os.getenv("BACKUP_DIR", "/backups")
RESTORE_DIR = os.getenv("RESTORE_DIR", "/restore")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))

# Ensure directories exist
Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)
Path(RESTORE_DIR).mkdir(parents=True, exist_ok=True)


class FortFailAgent:
    """FortFail backup and restore agent"""
    
    def __init__(self):
        self.agent_id = AGENT_ID
        self.orchestrator_url = ORCHESTRATOR_URL
        self.token = ORCH_JWT
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "POST", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def bootstrap_token(self):
        """Bootstrap JWT token if not provided"""
        if self.token:
            print(f"[{self.agent_id}] Using pre-provisioned JWT token")
            return
        
        print(f"[{self.agent_id}] Bootstrapping JWT token...")
        
        try:
            response = self.session.post(
                f"{self.orchestrator_url}/auth/token",
                json={
                    "registration_secret": AGENT_REG_SECRET,
                    "agent_id": self.agent_id
                },
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            self.token = data["token"]
            print(f"[{self.agent_id}] Token obtained, expires in {data['expires_in']}s")
        
        except Exception as e:
            print(f"[{self.agent_id}] Failed to bootstrap token: {e}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def create_snapshot(self, backup_path: str) -> Optional[str]:
        """Create snapshot from backup directory"""
        print(f"[{self.agent_id}] Creating snapshot from {backup_path}...")
        
        # Create tar archive
        snapshot_id = f"snapshot-{self.agent_id}-{int(time.time())}"
        tar_path = f"/tmp/{snapshot_id}.tar"
        
        try:
            with tarfile.open(tar_path, "w") as tar:
                tar.add(backup_path, arcname=".")
            
            # Compute checksum
            checksum = self._compute_checksum(tar_path)
            size = os.path.getsize(tar_path)
            
            print(f"[{self.agent_id}] Snapshot created: {snapshot_id} ({size} bytes, checksum: {checksum})")
            
            # Register snapshot metadata
            response = self.session.post(
                f"{self.orchestrator_url}/snapshots",
                json={
                    "id": snapshot_id,
                    "agent_id": self.agent_id,
                    "checksum": checksum,
                    "size": size,
                    "metadata": {"backup_path": backup_path}
                },
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            presigned_url = data.get("presigned_url")
            
            # Upload snapshot
            if presigned_url:
                print(f"[{self.agent_id}] Uploading via presigned URL...")
                self._upload_via_presigned_url(tar_path, presigned_url)
            else:
                print(f"[{self.agent_id}] Uploading via multipart POST...")
                self._upload_via_multipart(snapshot_id, tar_path)
            
            print(f"[{self.agent_id}] Snapshot uploaded successfully")
            
            # Clean up
            os.remove(tar_path)
            
            return snapshot_id
        
        except Exception as e:
            print(f"[{self.agent_id}] Failed to create snapshot: {e}")
            if os.path.exists(tar_path):
                os.remove(tar_path)
            return None
    
    def _compute_checksum(self, file_path: str) -> str:
        """Compute SHA256 checksum of file"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _upload_via_presigned_url(self, file_path: str, presigned_url: str):
        """Upload file via presigned URL"""
        with open(file_path, "rb") as f:
            response = self.session.put(
                presigned_url,
                data=f,
                timeout=300
            )
            response.raise_for_status()
    
    def _upload_via_multipart(self, snapshot_id: str, file_path: str):
        """Upload file via multipart POST"""
        with open(file_path, "rb") as f:
            response = self.session.post(
                f"{self.orchestrator_url}/snapshots/{snapshot_id}/object",
                files={"file": f},
                headers=self._get_headers(),
                timeout=300
            )
            response.raise_for_status()
    
    def poll_commands(self):
        """Poll for pending commands"""
        try:
            response = self.session.get(
                f"{self.orchestrator_url}/agent/{self.agent_id}/commands",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            
            commands = response.json()
            
            for cmd in commands:
                self._execute_command(cmd)
        
        except Exception as e:
            print(f"[{self.agent_id}] Failed to poll commands: {e}")
    
    def _execute_command(self, command: Dict[str, Any]):
        """Execute a command"""
        cmd_type = command["command_type"]
        payload = command["payload"]
        
        print(f"[{self.agent_id}] Executing command: {cmd_type}")
        
        if cmd_type == "restore":
            self._perform_restore(payload)
        else:
            print(f"[{self.agent_id}] Unknown command type: {cmd_type}")
    
    def _perform_restore(self, payload: Dict[str, Any]):
        """Perform restore operation"""
        snapshot_id = payload["snapshot_id"]
        job_id = payload["job_id"]
        
        print(f"[{self.agent_id}] Restoring snapshot {snapshot_id} for job {job_id}...")
        
        # Post start event
        self._post_event(
            job_id=job_id,
            snapshot_id=snapshot_id,
            event_type="restore_started",
            message=f"Starting restore of snapshot {snapshot_id}"
        )
        
        try:
            # Download snapshot
            tar_path = f"/tmp/restore-{snapshot_id}.tar"
            
            print(f"[{self.agent_id}] Downloading snapshot...")
            response = self.session.get(
                f"{self.orchestrator_url}/snapshots/{snapshot_id}/object",
                headers=self._get_headers(),
                stream=True,
                timeout=300
            )
            response.raise_for_status()
            
            with open(tar_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"[{self.agent_id}] Snapshot downloaded, extracting...")
            
            # Extract safely
            restore_path = Path(RESTORE_DIR) / snapshot_id
            restore_path.mkdir(parents=True, exist_ok=True)
            
            with tarfile.open(tar_path, "r") as tar:
                # Safe extraction (avoid path traversal)
                for member in tar.getmembers():
                    if member.name.startswith('/') or '..' in member.name:
                        print(f"[{self.agent_id}] Skipping unsafe path: {member.name}")
                        continue
                    tar.extract(member, path=restore_path)
            
            # Clean up
            os.remove(tar_path)
            
            print(f"[{self.agent_id}] Restore completed successfully")
            
            # Post completion event
            self._post_event(
                job_id=job_id,
                snapshot_id=snapshot_id,
                event_type="restore_completed",
                message=f"Restore completed to {restore_path}",
                metadata={"restore_path": str(restore_path)}
            )
        
        except Exception as e:
            print(f"[{self.agent_id}] Restore failed: {e}")
            
            # Post failure event
            self._post_event(
                job_id=job_id,
                snapshot_id=snapshot_id,
                event_type="restore_failed",
                message=f"Restore failed: {str(e)}"
            )
    
    def _post_event(
        self,
        event_type: str,
        message: str,
        job_id: Optional[str] = None,
        snapshot_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Post event to orchestrator"""
        try:
            self.session.post(
                f"{self.orchestrator_url}/agent/{self.agent_id}/events",
                json={
                    "job_id": job_id,
                    "snapshot_id": snapshot_id,
                    "event_type": event_type,
                    "message": message,
                    "metadata": metadata
                },
                headers=self._get_headers(),
                timeout=10
            )
        except Exception as e:
            print(f"[{self.agent_id}] Failed to post event: {e}")
    
    def run(self):
        """Main agent loop"""
        print(f"[{self.agent_id}] Starting FortFail Agent...")
        
        # Bootstrap token
        self.bootstrap_token()
        
        # Create initial snapshot if backup directory has content
        backup_path = Path(BACKUP_DIR)
        if backup_path.exists() and any(backup_path.iterdir()):
            self.create_snapshot(str(backup_path))
        
        # Main loop: poll for commands
        print(f"[{self.agent_id}] Polling for commands every {POLL_INTERVAL}s...")
        
        while True:
            try:
                self.poll_commands()
            except Exception as e:
                print(f"[{self.agent_id}] Error in main loop: {e}")
            
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    agent = FortFailAgent()
    agent.run()
