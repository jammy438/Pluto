from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, validator
from .base import DomainEntity
from .venue import Venue


class Game(DomainEntity):
    """Game domain model."""
    
    id: int = Field(..., description="Unique game identifier")
    home_team: str = Field(..., min_length=1, max_length=100, description="Home team name")
    away_team: str = Field(..., min_length=1, max_length=100, description="Away team name")
    game_date: Optional[date] = Field(None, description="Game date")
    venue_id: int = Field(..., description="Venue identifier")
    venue_name: Optional[str] = Field(None, description="Venue name (joined from venue)")
    
    @validator('home_team', 'away_team')
    def validate_team_names(cls, v):
        """Validate team names."""
        if not v or not v.strip():
            raise ValueError("Team name cannot be empty")
        return v.strip()
    
    @validator('away_team')
    def validate_different_teams(cls, v, values):
        """Ensure home and away teams are different."""
        if 'home_team' in values and v == values['home_team']:
            raise ValueError("Home and away teams must be different")
        return v
    
    def __str__(self) -> str:
        return f"Game(id={self.id}, {self.home_team} vs {self.away_team})"


class GameCreate(BaseModel):
    """Model for creating a new game."""
    home_team: str = Field(..., min_length=1, max_length=100)
    away_team: str = Field(..., min_length=1, max_length=100)
    game_date: Optional[date] = None
    venue_id: int


class GameUpdate(BaseModel):
    """Model for updating game."""
    home_team: Optional[str] = Field(None, min_length=1, max_length=100)
    away_team: Optional[str] = Field(None, min_length=1, max_length=100)
    game_date: Optional[date] = None
    venue_id: Optional[int] = None


class GameWithVenue(Game):
    """Game model with venue details."""
    venue: Optional[Venue] = None

