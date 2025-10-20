from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.settings import app_settings, settings
from app.middleware.custom import LoggingMiddleware
from app.routes.ai import router as ai_router
from app.routes.data import router as data_router
from app.routes.main import router as main_router
from app.utils.data_loader import validate_data_directory
from app.utils.logger import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app):
    """Application lifespan context manager"""
    # Startup
    logger.info("Starting %s v%s", settings.app.name, settings.app.version)

    # Validate data directory
    if validate_data_directory():
        logger.info("Data directory validated: %s", app_settings.data_dir)
    else:
        logger.warning("Some data files may be missing under %s", app_settings.data_dir)

    logger.info("API docs available at http://localhost:%s/docs", settings.app.port)
    logger.info("ReDoc available at http://localhost:%s/redoc", settings.app.port)

    # Show AI configuration status
    ai_providers = [provider.value for provider in settings.ai.providers.keys()]
    if ai_providers:
        logger.info("AI providers configured: %s", ", ".join(ai_providers))
        logger.info("Primary AI provider: %s", settings.ai.primary_provider.value)
    else:
        logger.warning("No AI providers configured")

    yield

    # Shutdown
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app.name,
    description="Backend API for theaditya.vercel.app portfolio website with AI-powered content management",
    version=settings.app.version,
    debug=settings.app.debug,
    lifespan=lifespan
)

static_directory = app_settings.static_dir
if static_directory.exists():
    asset_path = app_settings.asset_path.strip('/')
    mount_path = f"/{asset_path or 'assets'}"
    app.mount(mount_path, StaticFiles(directory=static_directory), name="assets")
    logger.info("Static assets mounted at %s from %s", mount_path, static_directory)
else:
    logger.warning("Static asset directory not found: %s", static_directory)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(main_router, tags=["main"])
app.include_router(data_router, prefix="/api", tags=["data"])
app.include_router(ai_router, prefix="/ai", tags=["ai"])

# Add root endpoint for health check
@app.get("/", tags=["main"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.app.name} v{settings.app.version}",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload
    )
