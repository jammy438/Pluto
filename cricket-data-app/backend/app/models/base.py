from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class DomainEntity(BaseModel, ABC):
    """Base class for all domain entities."""
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True
        arbitrary_types_allowed = True


class Repository(ABC):
    """Base repository interface."""
    
    @abstractmethod
    async def find_by_id(self, entity_id: int) -> Optional[DomainEntity]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    async def find_all(self) -> list[DomainEntity]:
        """Find all entities."""
        pass
    
    @abstractmethod
    async def save(self, entity: DomainEntity) -> DomainEntity:
        """Save entity."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        """Delete entity by ID."""
        pass