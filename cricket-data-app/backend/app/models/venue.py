from typing import Optional
from pydantic import BaseModel, Field, validator
from .base import DomainEntity


class Venue(DomainEntity):
    """Venue domain model."""
    
    id: int = Field(..., description="Unique venue identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Venue name")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate venue name."""
        if not v or not v.strip():
            raise ValueError("Venue name cannot be empty")
        return v.strip()
    
    def __str__(self) -> str:
        return f"Venue(id={self.id}, name='{self.name}')"


class VenueCreate(BaseModel):
    """Model for creating a new venue."""
    name: str = Field(..., min_length=1, max_length=200)


class VenueUpdate(BaseModel):
    """Model for updating venue."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)

