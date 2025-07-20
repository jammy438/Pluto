

# app/services/simulation_service.py
"""Simulation business logic service."""

from typing import List, Dict
from collections import Counter
from ..models.simulation import TeamSimulation
from ..database.repositories.simulation_repository import SimulationRepository
from ..constants import BusinessLogic


class SimulationService:
    """Service for simulation-related business logic."""
    
    def __init__(self, simulation_repo: SimulationRepository):
        self.simulation_repo = simulation_repo
    
    async def get_team_simulations(self, team_name: str) -> List[TeamSimulation]:
        """Get all simulations for a team."""
        return await self.simulation_repo.find_by_team(team_name)
    
    async def get_all_team_names(self) -> List[str]:
        """Get all unique team names."""
        return await self.simulation_repo.get_team_names()
    
    async def get_team_score_distribution(self, team_name: str) -> Dict[int, int]:
        """Get score distribution for a team."""
        distribution = await self.simulation_repo.get_score_distribution(team_name)
        return dict(distribution)
    
    async def get_team_statistics(self, team_name: str) -> Dict[str, float]:
        """Calculate team statistics."""
        simulations = await self.get_team_simulations(team_name)
        
        if not simulations:
            return {}
        
        scores = [sim.results for sim in simulations]
        
        # Calculate statistics
        total_games = len(scores)
        avg_score = sum(scores) / total_games
        min_score = min(scores)
        max_score = max(scores)
        
        # Calculate standard deviation
        variance = sum((score - avg_score) ** 2 for score in scores) / total_games
        std_dev = variance ** 0.5
        
        return {
            "total_simulations": total_games,
            "average_score": round(avg_score, BusinessLogic.WinProbability.DECIMAL_PLACES),
            "min_score": min_score,
            "max_score": max_score,
            "standard_deviation": round(std_dev, BusinessLogic.WinProbability.DECIMAL_PLACES)
        }
