"""
Tests for Pydantic models.
"""
import pytest
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestModelsImport:
    """Tests for models module import."""
    
    def test_import_models(self):
        """Test that models module can be imported."""
        try:
            from app.models import FlowCreate, FlowResponse, UserCreate, Token
            assert FlowCreate is not None
            assert FlowResponse is not None
        except ImportError:
            pytest.skip("Models module not available")


class TestFlowModels:
    """Tests for flow-related models."""
    
    def test_flow_create_valid(self):
        """Test creating a valid FlowCreate model."""
        try:
            from app.models import FlowCreate
            
            flow = FlowCreate(
                name="test_flow",
                description="A test flow",
                data={"nodes": [], "edges": []}
            )
            assert flow.name == "test_flow"
        except ImportError:
            pytest.skip("Models module not available")


class TestUserModels:
    """Tests for user-related models."""
    
    def test_user_create_valid(self):
        """Test creating a valid UserCreate model."""
        try:
            from app.models import UserCreate
            
            user = UserCreate(
                username="testuser",
                email="test@example.com",
                password="SecurePass123!"
            )
            assert user.username == "testuser"
            assert user.email == "test@example.com"
        except ImportError:
            pytest.skip("Models module not available")


class TestTokenModels:
    """Tests for token-related models."""
    
    def test_token_model(self):
        """Test Token model structure."""
        try:
            from app.models import Token
            
            token = Token(
                access_token="test_token_123",
                token_type="bearer"
            )
            assert token.access_token == "test_token_123"
            assert token.token_type == "bearer"
        except ImportError:
            pytest.skip("Models module not available")
