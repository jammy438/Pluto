import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import create_app
from app.database.connection import db_manager
from app.services.data_loader import DataLoaderService


class TestIntegration:
    """Integration tests."""
    
    def setup_method(self):
        """Setup integration test environment."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        
        # Create app with test database
        with patch('app.config.get_environment_settings') as mock_config:
            mock_config.return_value.database_path = self.test_db_path
            self.app = create_app()
            self.client = TestClient(self.app)
    
    def teardown_method(self):
        """Clean up integration test environment."""
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def test_full_application_flow(self):
        """Test complete application workflow."""
        # Test that application starts correctly
        response = self.client.get("/")
        assert response.status_code == 200
        
        # Test health check
        response = self.client.get("/health")
        assert response.status_code == 200
        
        # Test data status endpoint
        response = self.client.get("/debug/data-status")
        assert response.status_code == 200
        
        # Test venues endpoint (should be empty initially)
        response = self.client.get("/venues/")
        assert response.status_code == 200
        assert response.json() == []

