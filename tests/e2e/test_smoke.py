"""End-to-end smoke tests."""
import pytest
import httpx


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_service_is_accessible():
    """Test that the service is accessible."""
    # This test should run against a deployed instance
    # For local testing, ensure docker-compose is running
    
    base_url = "http://localhost:8080"
    
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        try:
            response = await client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            
        except httpx.ConnectError:
            pytest.skip("Service not running - expected for unit test environment")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_full_workflow():
    """Test a complete workflow through the system."""
    # This would test a full agent task execution
    # Skipped in unit test environment
    pytest.skip("Full workflow test requires deployed environment")
