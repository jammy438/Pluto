import sqlite3
from typing import List, Optional
from datetime import datetime
from ..connection import db_manager
from ...models.game import Game
from ...constants import Database
from .base import SQLiteRepository


class GameRepository(SQLiteRepository[Game]):
    """Repository for game data access."""
    
    def __init__(self):
        super().__init__(db_manager)
    
    @property
    def table_name(self) -> str:
        return Database.Tables.GAMES
    
    @property
    def model_class(self) -> type[Game]:
        return Game
    
    def _row_to_model(self, row: sqlite3.Row) -> Game:
        """Convert database row to Game model."""
        game_date = None
        if row.get(Database.Columns.DATE):
            try:
                game_date = datetime.strptime(row[Database.Columns.DATE], "%Y-%m-%d").date()
            except (ValueError, TypeError):
                pass
        
        return Game(
            id=row[Database.Columns.GAME_ID],
            home_team=row[Database.Columns.HOME_TEAM],
            away_team=row[Database.Columns.AWAY_TEAM],
            game_date=game_date,
            venue_id=row[Database.Columns.GAME_VENUE_ID],
            venue_name=row.get(Database.Columns.VENUE_NAME)  # From JOIN
        )
    
    async def find_with_venue(self, game_id: int) -> Optional[Game]:
        """Find game with venue information."""
        async with self.db_manager.get_async_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT g.*, v.{Database.Columns.VENUE_NAME}
                FROM {Database.Tables.GAMES} g
                JOIN {Database.Tables.VENUES} v ON g.{Database.Columns.GAME_VENUE_ID} = v.{Database.Columns.VENUE_ID}
                WHERE g.{Database.Columns.GAME_ID} = ?
            """, (game_id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None
    
    async def find_all_with_venues(self) -> List[Game]:
        """Find all games with venue information."""
        async with self.db_manager.get_async_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT g.*, v.{Database.Columns.VENUE_NAME}
                FROM {Database.Tables.GAMES} g
                JOIN {Database.Tables.VENUES} v ON g.{Database.Columns.GAME_VENUE_ID} = v.{Database.Columns.VENUE_ID}
                ORDER BY g.{Database.Columns.GAME_ID}
            """)
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
    
    async def find_by_teams(self, home_team: str, away_team: str) -> List[Game]:
        """Find games by team names."""
        async with self.db_manager.get_async_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT g.*, v.{Database.Columns.VENUE_NAME}
                FROM {Database.Tables.GAMES} g
                JOIN {Database.Tables.VENUES} v ON g.{Database.Columns.GAME_VENUE_ID} = v.{Database.Columns.VENUE_ID}
                WHERE g.{Database.Columns.HOME_TEAM} = ? AND g.{Database.Columns.AWAY_TEAM} = ?
            """, (home_team, away_team))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]

