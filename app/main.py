from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.routes.main import router as main_router
from app.routes.data import router as data_router
from app.routes.ai import router as ai_router
from app.middleware.custom import LoggingMiddleware
from app.utils.data_loader import setup_logging, validate_data_directory

# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app):
    """Application lifespan context manager"""
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")

    # Validate data directory
    if validate_data_directory():
        print("✅ Data directory validated successfully")
    else:
        print("⚠️  Warning: Some data files may be missing")

    print(f"📚 API Documentation available at: http://localhost:{settings.port}/docs")
    print(f"🔄 ReDoc available at: http://localhost:{settings.port}/redoc")

    yield

    # Shutdown
    print("🛑 Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Backend API for theaditya.vercel.app portfolio website",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
