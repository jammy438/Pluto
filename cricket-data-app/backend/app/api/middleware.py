from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..config import get_environment_settings
from ..constants import API


def setup_middleware(app: FastAPI) -> None:
    """Setup middleware for the FastAPI application."""
    config = get_environment_settings()
    
    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins_list,
        allow_credentials=config.cors_allow_credentials,
        allow_methods=API.CORS.ALLOWED_METHODS,
        allow_headers=API.CORS.ALLOWED_HEADERS,
    )

