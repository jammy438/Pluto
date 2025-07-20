# app/services/game_service.py
"""Game business logic service."""

from typing import List, Optional
from ..models.game import Game
from ..models.simulation import GameAnalysis, HistogramData, Simulation
from ..database.repositories.game_repository import GameRepository
from ..database.repositories.simulation_repository import SimulationRepository
from ..constants import BusinessLogic, ErrorMessages
from collections import Counter
import math


class GameService:
    """Service for game-related business logic."""
    
    def __init__(self, game_repo: GameRepository, simulation_repo: SimulationRepository):
        self.game_repo = game_repo
        self.simulation_repo = simulation_repo
    
    async def get_all_games(self) -> List[Game]:
        """Get all games with venue information."""
        return await self.game_repo.find_all_with_venues()
    
    async def get_game_by_id(self, game_id: int) -> Optional[Game]:
        """Get game by ID with venue information."""
        return await self.game_repo.find_with_venue(game_id)
    
    async def get_game_analysis(self, game_id: int) -> Optional[GameAnalysis]:
        """Get complete game analysis with simulations and win probability."""
        game = await self.get_game_by_id(game_id)
        if not game:
            return None
        
        simulations = await self.simulation_repo.get_game_simulations(
            game.home_team, game.away_team
        )
        
        if not simulations:
            return None
        
        home_wins = sum(1 for sim in simulations if sim.home_wins)
        total_sims = len(simulations)
        win_probability = round(
            (home_wins / total_sims) * BusinessLogic.WinProbability.PERCENTAGE_MULTIPLIER,
            BusinessLogic.WinProbability.DECIMAL_PLACES
        )
        
        return GameAnalysis(
            game_id=game_id,
            simulations=simulations,
            home_win_probability=win_probability,
            total_simulations=total_sims
        )
    
    async def get_histogram_data(self, game_id: int) -> Optional[HistogramData]:
        """Get histogram data for game visualization."""
        game = await self.get_game_by_id(game_id)
        if not game:
            return None
        
        home_simulations = await self.simulation_repo.find_by_team(game.home_team)
        away_simulations = await self.simulation_repo.find_by_team(game.away_team)
        
        if not home_simulations or not away_simulations:
            return None
        
        home_scores = [sim.results for sim in home_simulations]
        away_scores = [sim.results for sim in away_simulations]
        
        all_scores = home_scores + away_scores
        score_range = (min(all_scores), max(all_scores))
        
        return HistogramData(
            home_team=game.home_team,
            away_team=game.away_team,
            home_scores=home_scores,
            away_scores=away_scores,
            score_range=score_range
        )
    
    async def find_games_by_teams(self, home_team: str, away_team: str) -> List[Game]:
        """Find games by team names."""
        return await self.game_repo.find_by_teams(home_team, away_team)
