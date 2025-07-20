from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from ...models.venue import Venue
from ...models.game import Game
from ...models.simulation import Simulation


class VenueResponse(BaseModel):
    """Venue API response model."""
    id: int
    name: str


class GameResponse(BaseModel):
    """Game API response model."""
    id: int
    home_team: str
    away_team: str
    date: Optional[str] = None
    venue_id: int
    venue_name: str


class SimulationResponse(BaseModel):
    """Simulation API response model."""
    home_score: int
    away_score: int


class GameAnalysisResponse(BaseModel):
    """Game analysis API response model."""
    game: GameResponse
    simulations: List[SimulationResponse]
    home_win_probability: float
    total_simulations: int


class HistogramDataResponse(BaseModel):
    """Histogram data API response model."""
    home_team: str
    away_team: str
    home_scores: List[int]
    away_scores: List[int]
    score_range: tuple[int, int]


class TeamSimulationResponse(BaseModel):
    """Team simulation API response model."""
    team_id: int
    team: str
    simulation_run: int
    results: int


class TeamStatisticsResponse(BaseModel):
    """Team statistics API response model."""
    total_simulations: int
    average_score: float
    min_score: int
    max_score: int
    standard_deviation: float


class HealthResponse(BaseModel):
    """Health check API response model."""
    status: str
    database: str
    timestamp: str


class DataStatusResponse(BaseModel):
    """Data status API response model."""
    config: Dict[str, Any]
    files_status: Dict[str, bool]
    tables_info: Dict[str, Dict[str, Any]]


class APIInfoResponse(BaseModel):
    """API info response model."""
    message: str
    environment: str
    version: str

