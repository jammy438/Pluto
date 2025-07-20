import pytest
import asyncio
import tempfile
import os
from unittest.mock import patch


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_database():
    """Provide a temporary test database."""
    test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    test_db_path = test_db.name
    test_db.close()
    
    yield test_db_path
    
    if os.path.exists(test_db_path):
        os.unlink(test_db_path)


@pytest.fixture
def mock_config(test_database):
    """Provide mock configuration for testing."""
    with patch('app.config.get_environment_settings') as mock:
        mock.return_value.database_path = test_database
        mock.return_value.api_title = "Test Cricket API"
        mock.return_value.api_version = "1.0.0"
        mock.return_value.environment = "testing"
        yield mock.return_value

