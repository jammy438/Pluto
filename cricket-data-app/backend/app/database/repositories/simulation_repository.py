import sqlite3
from typing import List, Dict
from collections import Counter
from ..connection import db_manager
from ...models.simulation import TeamSimulation, Simulation
from ...constants import Database
from .base import SQLiteRepository


class SimulationRepository(SQLiteRepository[TeamSimulation]):
    """Repository for simulation data access."""
    
    def __init__(self):
        super().__init__(db_manager)
    
    @property
    def table_name(self) -> str:
        return Database.Tables.SIMULATIONS
    
    @property
    def model_class(self) -> type[TeamSimulation]:
        return TeamSimulation
    
    def _row_to_model(self, row: sqlite3.Row) -> TeamSimulation:
        """Convert database row to TeamSimulation model."""
        return TeamSimulation(
            team_id=row[Database.Columns.TEAM_ID],
            team=row[Database.Columns.TEAM],
            simulation_run=row[Database.Columns.SIMULATION_RUN],
            results=row[Database.Columns.RESULTS]
        )
    
    async def find_by_team(self, team_name: str) -> List[TeamSimulation]:
        """Find simulations by team name."""
        async with self.db_manager.get_async_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE {Database.Columns.TEAM} = ? ORDER BY {Database.Columns.SIMULATION_RUN}",
                (team_name,)
            )
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
    
    async def get_game_simulations(self, home_team: str, away_team: str) -> List[Simulation]:
        """Get paired simulations for a game."""
        async with self.db_manager.get_async_connection() as conn:
            cursor = conn.cursor()
            
            # Get simulation runs that exist for both teams
            cursor.execute(f"""
                SELECT DISTINCT h.{Database.Columns.SIMULATION_RUN}
                FROM {self.table_name} h
                JOIN {self.table_name} a ON h.{Database.Columns.SIMULATION_RUN} = a.{Database.Columns.SIMULATION_RUN}
                WHERE h.{Database.Columns.TEAM} = ? AND a.{Database.Columns.TEAM} = ?
                ORDER BY h.{Database.Columns.SIMULATION_RUN}
            """, (home_team, away_team))
            
            simulation_runs = [row[0] for row in cursor.fetchall()]
            
            simulations = []
            for run in simulation_runs:
                # Get scores for both teams in this simulation run
                cursor.execute(f"""
                    SELECT {Database.Columns.TEAM}, {Database.Columns.RESULTS}
                    FROM {self.table_name}
                    WHERE {Database.Columns.SIMULATION_RUN} = ? 
                    AND {Database.Columns.TEAM} IN (?, ?)
                """, (run, home_team, away_team))
                
                scores = dict(cursor.fetchall())
                if home_team in scores and away_team in scores:
                    simulations.append(Simulation(
                        home_score=scores[home_team],
                        away_score=scores[away_team]
                    ))
            
            return simulations
    
    async def get_team_names(self) -> List[str]:
        """Get all unique team names."""
        async with self.db_manager.get_async_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT DISTINCT {Database.Columns.TEAM} FROM {self.table_name}")
            return [row[0] for row in cursor.fetchall()]
    
    async def get_score_distribution(self, team_name: str) -> Counter:
        """Get score distribution for a team."""
        simulations = await self.find_by_team(team_name)
        return Counter(sim.results for sim in simulations)