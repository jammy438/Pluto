# main.py
"""
Cricket Data App - FastAPI Application with Enhanced Logging
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import traceback
import sys
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import configuration and dependencies with error handling
try:
    from app.config import get_environment_settings
    config = get_environment_settings()
    logger.info("Config loaded successfully")
except Exception as e:
    logger.error(f"Config import error: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    # Fallback config
    class FallbackConfig:
        api_title = "Cricket Data App"
        api_version = "1.0.0"
        api_debug = True
        api_host = "0.0.0.0"
        api_port = 8000
        api_reload = True
        environment = "development"
        database_path = "cricket_data.db"
    config = FallbackConfig()

try:
    from app.database.connection import db_manager
    logger.info("Database manager loaded")
except Exception as e:
    logger.error(f"Database manager import error: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    db_manager = None

try:
    from app.services.data_loader import DataLoaderService
    logger.info("Data loader service loaded")
except Exception as e:
    logger.error(f"Data loader service import error: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    DataLoaderService = None

try:
    from app.api.middleware import setup_middleware
    logger.info("Middleware loaded")
except Exception as e:
    logger.error(f"Middleware import error: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    def setup_middleware(app):
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

# Import API routers with error handling
routers_to_load = []

try:
    from app.api.endpoints.root import router as root_router
    routers_to_load.append(("root", root_router, ""))
    logger.info("Root router loaded")
except Exception as e:
    logger.error(f"Root router import error: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")

try:
    from app.api.endpoints.venues import router as venues_router
    routers_to_load.append(("venues", venues_router, ""))
    logger.info("Venues router loaded")
except Exception as e:
    logger.error(f"Venues router import error: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")

try:
    from app.api.endpoints.games import router as games_router
    routers_to_load.append(("games", games_router, ""))
    logger.info("Games router loaded")
except Exception as e:
    logger.error(f"Games router import error: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")

try:
    from app.api.endpoints.simulations import router as simulations_router
    routers_to_load.append(("simulations", simulations_router, ""))
    logger.info("Simulations router loaded")
except Exception as e:
    logger.error(f"Simulations router import error: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Starting Cricket Data App...")
    
    try:
        # Initialize database
        if db_manager:
            logger.info("Initializing database...")
            db_manager.init_database()
            logger.info("Database initialized")
        else:
            logger.warning("Database manager not available")
        
        # Load CSV data
        if DataLoaderService:
            logger.info("Loading CSV data...")
            data_loader = DataLoaderService()
            result = data_loader.load_all_csv_data()
            if result:
                logger.info("CSV data loaded successfully")
            else:
                logger.warning("CSV data loading had issues")
        else:
            logger.warning("Data loader service not available")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Cricket Data App...")


# Global exception handler
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception in {request.method} {request.url}")
    logger.error(f"Exception type: {type(exc).__name__}")
    logger.error(f"Exception message: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "path": str(request.url.path),
            "method": request.method
        }
    )


# Request logging middleware
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()
    
    logger.info(f"Incoming request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} | Time: {process_time:.3f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request failed: {request.method} {request.url}")
        logger.error(f"Error: {str(e)} | Time: {process_time:.3f}s")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    logger.info("Creating FastAPI application...")
    
    # Initialize FastAPI app
    app = FastAPI(
        title=config.api_title,
        version=config.api_version,
        debug=config.api_debug,
        lifespan=lifespan,
        description="Cricket Simulation Analysis API - Layered Architecture"
    )
    
    # Add global exception handler
    app.add_exception_handler(Exception, global_exception_handler)
    
    # Add request logging middleware
    app.middleware("http")(log_requests)
    
    # Setup middleware
    try:
        setup_middleware(app)
        logger.info("Middleware configured")
    except Exception as e:
        logger.error(f"Middleware setup error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Include routers
    for name, router, prefix in routers_to_load:
        try:
            if prefix:
                app.include_router(router, prefix=prefix)
                logger.info(f"{name.capitalize()} router included with prefix '{prefix}'")
            else:
                app.include_router(router)
                logger.info(f"{name.capitalize()} router included")
            
            # Log the routes in this router
            for route in router.routes:
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    methods = getattr(route, 'methods', ['GET'])
                    logger.info(f"  Route: {methods} {prefix}{route.path}")
        except Exception as e:
            logger.error(f"Error including {name} router: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Log all available routes
    logger.info("All registered routes:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = getattr(route, 'methods', ['GET'])
            logger.info(f"  {methods} {route.path}")
    
    return app


# Create the app instance
logger.info("Creating app instance...")
app = create_app()
logger.info("App instance created successfully")


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Cricket Data App starting on {config.api_host}:{config.api_port}")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Database: {config.database_path}")
    logger.info(f"Reload: {config.api_reload}")
    
    try:
        uvicorn.run(
            "main:app",
            host=config.api_host,
            port=config.api_port,
            reload=config.api_reload,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)