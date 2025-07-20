from typing import Annotated
from fastapi import Depends
from app.database.repositories.venue_repository import VenueRepository
from app.database.repositories.game_repository import GameRepository
from app.database.repositories.simulation_repository import SimulationRepository
from app.services.venue_service import VenueService
from app.services.game_service import GameService
from app.services.simulation_service import SimulationService
from app.services.data_loader import DataLoaderService

# Repository dependencies
def get_venue_repository() -> VenueRepository:
    """Get venue repository instance."""
    return VenueRepository()


def get_game_repository() -> GameRepository:
    """Get game repository instance."""
    return GameRepository()


def get_simulation_repository() -> SimulationRepository:
    """Get simulation repository instance."""
    return SimulationRepository()


# Service dependencies
def get_venue_service(
    venue_repo: Annotated[VenueRepository, Depends(get_venue_repository)]
) -> VenueService:
    """Get venue service instance."""
    return VenueService(venue_repo)


def get_game_service(
    game_repo: Annotated[GameRepository, Depends(get_game_repository)],
    simulation_repo: Annotated[SimulationRepository, Depends(get_simulation_repository)]
) -> GameService:
    """Get game service instance."""
    return GameService(game_repo, simulation_repo)


def get_simulation_service(
    simulation_repo: Annotated[SimulationRepository, Depends(get_simulation_repository)]
) -> SimulationService:
    """Get simulation service instance."""
    return SimulationService(simulation_repo)


def get_data_loader_service() -> DataLoaderService:
    """Get data loader service instance."""
    return DataLoaderService()
