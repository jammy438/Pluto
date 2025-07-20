from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from ...constants import HTTPStatus, API, Database
from ...services.data_loader import DataLoaderService
from ..dependencies import get_data_loader_service
from ..responses.models import APIInfoResponse, HealthResponse, DataStatusResponse
from ...config import get_environment_settings

router = APIRouter()


@router.get("/", response_model=APIInfoResponse)
async def root():
    """Root endpoint returning API status."""
    config = get_environment_settings()
    return APIInfoResponse(
        message=API.ResponseMessages.API_RUNNING.format(title=config.api_title),
        environment=config.environment,
        version=config.api_version
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status=API.ResponseMessages.HEALTH_STATUS_HEALTHY,
        database=API.ResponseMessages.DATABASE_CONNECTED,
        timestamp=datetime.now().isoformat()
    )


@router.get("/debug/data-status", response_model=DataStatusResponse)
async def debug_data_status(
    data_loader: Annotated[DataLoaderService, Depends(get_data_loader_service)]
):
    """Debug endpoint to check data loading status."""
    status = data_loader.get_data_status()
    return DataStatusResponse(**status)

