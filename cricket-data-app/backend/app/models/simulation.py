from typing import Optional, List
from pydantic import Field, validator
from .base import DomainEntity


class Simulation(DomainEntity):
    """Individual simulation result."""
    
    home_score: int = Field(..., ge=0, le=500, description="Home team score")
    away_score: int = Field(..., ge=0, le=500, description="Away team score")
    
    @property
    def home_wins(self) -> bool:
        """Check if home team wins."""
        return self.home_score > self.away_score
    
    def __str__(self) -> str:
        return f"Simulation({self.home_score}-{self.away_score})"


class TeamSimulation(DomainEntity):
    """Team simulation data model."""
    
    team_id: int = Field(..., description="Team identifier")
    team: str = Field(..., min_length=1, description="Team name")
    simulation_run: int = Field(..., ge=1, description="Simulation run number")
    results: int = Field(..., ge=0, le=500, description="Score result")
    
    @validator('team')
    def validate_team_name(cls, v):
        """Validate team name."""
        if not v or not v.strip():
            raise ValueError("Team name cannot be empty")
        return v.strip()


class GameAnalysis(DomainEntity):
    """Complete game analysis with simulations."""
    
    game_id: int = Field(..., description="Game identifier")
    simulations: List[Simulation] = Field(..., description="All simulation results")
    home_win_probability: float = Field(..., ge=0, le=100, description="Home team win percentage")
    total_simulations: int = Field(..., ge=0, description="Total number of simulations")
    
    @validator('simulations')
    def validate_simulations(cls, v):
        """Validate simulations list."""
        if not v:
            raise ValueError("Simulations list cannot be empty")
        return v
    
    @property
    def home_wins(self) -> int:
        """Count of home team wins."""
        return sum(1 for sim in self.simulations if sim.home_wins)
    
    @property
    def away_wins(self) -> int:
        """Count of away team wins."""
        return self.total_simulations - self.home_wins


class HistogramData(DomainEntity):
    """Histogram visualization data."""
    
    home_team: str = Field(..., description="Home team name")
    away_team: str = Field(..., description="Away team name")
    home_scores: List[int] = Field(..., description="Home team score distribution")
    away_scores: List[int] = Field(..., description="Away team score distribution")
    score_range: tuple[int, int] = Field(..., description="Min and max scores")
    
    @validator('home_scores', 'away_scores')
    def validate_scores(cls, v):
        """Validate score lists."""
        if not v:
            raise ValueError("Score list cannot be empty")
        return v