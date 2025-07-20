import sqlite3
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from ..config import get_environment_settings
from ..constants import Database, Logging


class DatabaseManager:
    """Manages database connections and initialization."""
    
    def __init__(self):
        self.config = get_environment_settings()
        self._connection: Optional[sqlite3.Connection] = None
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        return sqlite3.connect(self.config.database_path)
    
    @asynccontextmanager
    async def get_async_connection(self) -> AsyncGenerator[sqlite3.Connection, None]:
        """Async context manager for database connections."""
        conn = None
        try:
            # Run in thread pool to avoid blocking
            conn = await asyncio.get_event_loop().run_in_executor(
                None, self.get_connection
            )
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        finally:
            if conn:
                conn.close()
    
    def init_database(self) -> None:
        """Initialize database with tables."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Create tables using constants
            cursor.execute(Database.Queries.CREATE_VENUES_TABLE)
            cursor.execute(Database.Queries.CREATE_GAMES_TABLE)
            cursor.execute(Database.Queries.CREATE_SIMULATIONS_TABLE)
            
            conn.commit()
            print(Logging.Messages.DATABASE_INITIALIZED)
        finally:
            conn.close()


# Singleton instance
db_manager = DatabaseManager()



