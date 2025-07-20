import pytest
from pydantic import ValidationError
from datetime import date
from app.models.venue import Venue, VenueCreate
from app.models.game import Game, GameCreate
from app.models.simulation import Simulation, TeamSimulation


class TestModels:
    """Test domain model validation and behavior."""
    
    def test_venue_model_validation(self):
        """Test venue model validation."""
        # Valid venue
        venue = Venue(id=1, name="Test Venue")
        assert venue.id == 1
        assert venue.name == "Test Venue"
        
        # Invalid venue - empty name
        with pytest.raises(ValidationError):
            Venue(id=1, name="")
        
        # Invalid venue - whitespace only name
        with pytest.raises(ValidationError):
            Venue(id=1, name="   ")
    
    def test_game_model_validation(self):
        """Test game model validation."""
        # Valid game
        game = Game(
            id=1,
            home_team="Team A",
            away_team="Team B",
            game_date=date.today(),
            venue_id=1
        )
        assert game.home_team == "Team A"
        assert game.away_team == "Team B"
        
        # Invalid game - same teams
        with pytest.raises(ValidationError):
            Game(
                id=1,
                home_team="Team A",
                away_team="Team A",
                venue_id=1
            )
        
        # Invalid game - empty team name
        with pytest.raises(ValidationError):
            Game(
                id=1,
                home_team="",
                away_team="Team B",
                venue_id=1
            )
    
    def test_simulation_model_behavior(self):
        """Test simulation model behavior."""
        # Home team wins
        sim = Simulation(home_score=150, away_score=140)
        assert sim.home_wins is True
        
        # Away team wins
        sim = Simulation(home_score=140, away_score=150)
        assert sim.home_wins is False
        
        # Tie (away team wins in cricket context)
        sim = Simulation(home_score=150, away_score=150)
        assert sim.home_wins is False
        
        # Invalid scores
        with pytest.raises(ValidationError):
            Simulation(home_score=-10, away_score=150)
        
        with pytest.raises(ValidationError):
            Simulation(home_score=150, away_score=600)  # Over max limit