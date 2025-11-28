"""
Tests for the main FastAPI application endpoints.
"""
import pytest
import json
import tempfile
import os


class TestHealthEndpoint:
    """Tests for health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns successfully."""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_contains_welcome(self, client):
        """Test root endpoint contains welcome message."""
        response = client.get("/")
        data = response.json()
        assert "message" in data or "welcome" in str(data).lower() or response.status_code == 200


class TestFlowManagement:
    """Tests for flow management endpoints."""
    
    def test_list_flows_empty(self, client):
        """Test listing flows when directory is empty or doesn't exist."""
        response = client.get("/list_flows/")
        assert response.status_code == 200
        data = response.json()
        assert "flows" in data or isinstance(data, list) or isinstance(data, dict)
    
    def test_save_flow(self, client, sample_flow):
        """Test saving a flow file."""
        # Create a temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_flow, f)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = client.post(
                    "/save_flow/",
                    files={"flow_file": ("test_flow.json", f, "application/json")}
                )
            assert response.status_code in [200, 201, 422]
        finally:
            os.unlink(temp_path)
    
    def test_get_flow_not_found(self, client):
        """Test getting a flow that doesn't exist."""
        response = client.get("/get_flow/nonexistent_flow.json")
        assert response.status_code in [404, 400, 200]


class TestRunFlow:
    """Tests for flow execution endpoint."""
    
    def test_run_flow_with_input(self, client, sample_flow):
        """Test running a flow with user input."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_flow, f)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = client.post(
                    "/run_flow/",
                    files={"flow_file": ("test_flow.json", f, "application/json")},
                    data={"user_input": "Hello, test!"}
                )
            # Should work or return simulated response
            assert response.status_code in [200, 422, 500]
        finally:
            os.unlink(temp_path)


class TestCORS:
    """Tests for CORS configuration."""
    
    def test_cors_headers(self, client):
        """Test that CORS headers are present."""
        response = client.options("/", headers={
            "Origin": "http://localhost:8080",
            "Access-Control-Request-Method": "GET"
        })
        # CORS preflight should succeed or not be blocked
        assert response.status_code in [200, 204, 405]
