import sqlite3
from typing import List, Optional
from ..connection import db_manager
from ...models.venue import Venue
from ...constants import Database
from .base import SQLiteRepository


class VenueRepository(SQLiteRepository[Venue]):
    """Repository for venue data access."""
    
    def __init__(self):
        super().__init__(db_manager)
    
    @property
    def table_name(self) -> str:
        return Database.Tables.VENUES
    
    @property
    def model_class(self) -> type[Venue]:
        return Venue
    
    def _row_to_model(self, row: sqlite3.Row) -> Venue:
        """Convert database row to Venue model."""
        return Venue(
            id=row[Database.Columns.VENUE_ID],
            name=row[Database.Columns.VENUE_NAME]
        )
    
    async def find_by_name(self, name: str) -> Optional[Venue]:
        """Find venue by name."""
        async with self.db_manager.get_async_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE {Database.Columns.VENUE_NAME} = ?",
                (name,)
            )
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None
