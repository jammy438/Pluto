import pytest
from unittest.mock import Mock, AsyncMock
from app.services.game_service import GameService
from app.services.venue_service import VenueService
from app.services.simulation_service import SimulationService
from app.models.venue import Venue
from app.models.game import Game
from app.models.simulation import TeamSimulation, Simulation


class TestServices:
    """Test service implementations."""
    
    def setup_method(self):
        """Setup mocks for each test."""
        self.mock_venue_repo = AsyncMock()
        self.mock_game_repo = AsyncMock()
        self.mock_simulation_repo = AsyncMock()
    
    @pytest.mark.asyncio
    async def test_venue_service(self):
        """Test venue service operations."""
        # Setup test data
        test_venue = Venue(id=1, name="Test Venue")
        self.mock_venue_repo.find_all.return_value = [test_venue]
        self.mock_venue_repo.find_by_id.return_value = test_venue
        
        # Create service
        service = VenueService(self.mock_venue_repo)
        
        # Test get_all_venues
        venues = await service.get_all_venues()
        assert len(venues) == 1
        assert venues[0].name == "Test Venue"
        self.mock_venue_repo.find_all.assert_called_once()
        
        # Test get_venue_by_id
        venue = await service.get_venue_by_id(1)
        assert venue.name == "Test Venue"
        self.mock_venue_repo.find_by_id.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_game_service(self):
        """Test game service operations."""
        # Setup test data
        test_game = Game(
            id=1,
            home_team="Team A",
            away_team="Team B",
            game_date=None,
            venue_id=1,
            venue_name="Test Venue"
        )
        
        test_simulations = [
            Simulation(home_score=150, away_score=140),
            Simulation(home_score=160, away_score=170),
            Simulation(home_score=155, away_score=145)
        ]
        
        self.mock_game_repo.find_with_venue.return_value = test_game
        self.mock_simulation_repo.get_game_simulations.return_value = test_simulations
        
        # Create service
        service = GameService(self.mock_game_repo, self.mock_simulation_repo)
        
        # Test get_game_analysis
        analysis = await service.get_game_analysis(1)
        assert analysis is not None
        assert analysis.game_id == 1
        assert analysis.total_simulations == 3
        assert analysis.home_win_probability == 66.67  # 2 out of 3 wins
        
        self.mock_game_repo.find_with_venue.assert_called_once_with(1)
        self.mock_simulation_repo.get_game_simulations.assert_called_once_with("Team A", "Team B")
    
    @pytest.mark.asyncio
    async def test_simulation_service(self):
        """Test simulation service operations."""
        # Setup test data
        test_simulations = [
            TeamSimulation(team_id=1, team="Team A", simulation_run=1, results=150),
            TeamSimulation(team_id=1, team="Team A", simulation_run=2, results=160),
            TeamSimulation(team_id=1, team="Team A", simulation_run=3, results=155)
        ]
        
        self.mock_simulation_repo.find_by_team.return_value = test_simulations
        
        # Create service
        service = SimulationService(self.mock_simulation_repo)
        
        # Test get_team_simulations
        simulations = await service.get_team_simulations("Team A")
        assert len(simulations) == 3
        assert simulations[0].results == 150
        
        # Test get_team_statistics
        stats = await service.get_team_statistics("Team A")
        assert stats["total_simulations"] == 3
        assert stats["average_score"] == 155.0
        assert stats["min_score"] == 150
        assert stats["max_score"] == 160

