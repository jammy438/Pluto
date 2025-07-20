import sqlite3
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from ...models.base import DomainEntity, Repository

T = TypeVar('T', bound=DomainEntity)


class SQLiteRepository(Repository, Generic[T], ABC):
    """Base SQLite repository implementation."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Table name for this repository."""
        pass
    
    @property
    @abstractmethod
    def model_class(self) -> type[T]:
        """Model class for this repository."""
        pass
    
    @abstractmethod
    def _row_to_model(self, row: sqlite3.Row) -> T:
        """Convert database row to model instance."""
        pass
    
    async def find_by_id(self, entity_id: int) -> Optional[T]:
        """Find entity by ID."""
        async with self.db_manager.get_async_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE id = ?",
                (entity_id,)
            )
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None
    
    async def find_all(self) -> List[T]:
        """Find all entities."""
        async with self.db_manager.get_async_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name}")
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
    
    async def save(self, entity: T) -> T:
        """Save entity (not implemented in base - override in concrete classes)."""
        raise NotImplementedError("Save method must be implemented by concrete repositories")
    
    async def delete(self, entity_id: int) -> bool:
        """Delete entity by ID."""
        async with self.db_manager.get_async_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM {self.table_name} WHERE id = ?",
                (entity_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
