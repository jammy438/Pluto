# tests/test_repositories.py
import pytest
import sqlite3
import tempfile
import os
from unittest.mock import patch, AsyncMock

from app.database.connection import DatabaseManager
from app.database.repositories.venue_repository import VenueRepository
from app.database.repositories.game_repository import GameRepository
from app.database.repositories.simulation_repository import SimulationRepository
from app.models.venue import Venue
from app.models.game import Game
from app.models.simulation import TeamSimulation


class TestRepositories:
    """Test repository implementations."""
    
    def setup_method(self):
        """Setup test database for each test."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        
        # Initialize test database
        self.db_manager = DatabaseManager()
        with patch.object(self.db_manager, 'config') as mock_config:
            mock_config.database_path = self.test_db_path
            self.db_manager.init_database()
    
    def teardown_method(self):
        """Clean up test database after each test."""
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    @pytest.mark.asyncio
    async def test_venue_repository(self):
        """Test venue repository operations."""
        repo = VenueRepository()
        
        # Mock the database manager
        with patch.object(repo, 'db_manager', self.db_manager):
            # Test find_all when empty
            venues = await repo.find_all()
            assert venues == []
            
            # Insert test data manually
            conn = sqlite3.connect(self.test_db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO venues (venue_id, venue_name) VALUES (1, 'Test Venue')")
            conn.commit()
            conn.close()
            
            # Test find_all with data
            venues = await repo.find_all()
            assert len(venues) == 1
            assert venues[0].id == 1
            assert venues[0].name == 'Test Venue'
            
            # Test find_by_id
            venue = await repo.find_by_id(1)
            assert venue is not None
            assert venue.name == 'Test Venue'
            
            # Test find_by_name
            venue = await repo.find_by_name('Test Venue')
            assert venue is not None
            assert venue.id == 1
