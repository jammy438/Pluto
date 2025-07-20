
from typing import List, Optional
from ..models.venue import Venue
from ..database.repositories.venue_repository import VenueRepository


class VenueService:
    """Service for venue-related business logic."""
    
    def __init__(self, venue_repo: VenueRepository):
        self.venue_repo = venue_repo
    
    async def get_all_venues(self) -> List[Venue]:
        """Get all venues."""
        return await self.venue_repo.find_all()
    
    async def get_venue_by_id(self, venue_id: int) -> Optional[Venue]:
        """Get venue by ID."""
        return await self.venue_repo.find_by_id(venue_id)
    
    async def get_venue_by_name(self, name: str) -> Optional[Venue]:
        """Get venue by name."""
        return await self.venue_repo.find_by_name(name)

