import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import create_app
from app.constants import HTTPStatus


class TestAPIEndpoints:
    """Test API endpoint implementations."""
    
    def setup_method(self):
        """Setup test client."""
        self.app = create_app()
        self.client = TestClient(self.app)
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = self.client.get("/")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert "message" in data
        assert "environment" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    @patch('app.services.venue_service.VenueService.get_all_venues')
    def test_venues_endpoint(self, mock_get_venues):
        """Test venues endpoint."""
        # Mock the service response
        mock_venues = [
            {"id": 1, "name": "Test Venue 1"},
            {"id": 2, "name": "Test Venue 2"}
        ]
        mock_get_venues.return_value = [
            type('Venue', (), venue)() for venue in mock_venues
        ]
        
        response = self.client.get("/venues/")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Test Venue 1"
    
    @patch('app.services.game_service.GameService.get_all_games')
    def test_games_endpoint(self, mock_get_games):
        """Test games endpoint."""
        # Mock the service response
        mock_game = type('Game', (), {
            'id': 1,
            'home_team': 'Team A',
            'away_team': 'Team B',
            'game_date': None,
            'venue_id': 1,
            'venue_name': 'Test Venue'
        })()
        mock_get_games.return_value = [mock_game]
        
        response = self.client.get("/games/")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["home_team"] == "Team A"

