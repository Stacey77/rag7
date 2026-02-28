"""Test task management and ack flow."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    """Test task creation."""
    # Login first
    login_response = await client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass"}
    )
    token = login_response.json()["access_token"]
    
    # Create task
    response = await client.post(
        "/decisions/task",
        json={
            "task_type": "test_decision",
            "input_data": {"test": "data"},
            "priority": 1
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["task_type"] == "test_decision"
    assert data["state"] == "queued"


@pytest.mark.asyncio
async def test_get_task(client: AsyncClient):
    """Test get task endpoint."""
    # Login
    login_response = await client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass"}
    )
    token = login_response.json()["access_token"]
    
    # Create task
    create_response = await client.post(
        "/decisions/task",
        json={
            "task_type": "test_decision",
            "input_data": {"test": "data"}
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    task_id = create_response.json()["task_id"]
    
    # Get task
    response = await client.get(
        f"/decisions/task/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
