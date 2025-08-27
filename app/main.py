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
    print(f"🚀 Starting {settings.app.name} v{settings.app.version}")
    
    # Validate data directory
    if validate_data_directory():
        print("✅ Data directory validated successfully")
    else:
        print("⚠️  Warning: Some data files may be missing")
    
    print(f"📚 API Documentation available at: http://localhost:{settings.app.port}/docs")
    print(f"🔄 ReDoc available at: http://localhost:{settings.app.port}/redoc")
    
    # Show AI configuration status
    ai_providers = list(settings.ai.providers.keys())
    if ai_providers:
        print(f"🤖 AI Providers configured: {', '.join([p.value for p in ai_providers])}")
        print(f"🎯 Primary AI Provider: {settings.ai.primary_provider.value}")
    else:
        print("⚠️  Warning: No AI providers configured")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.app.name,
    description="Backend API for theaditya.vercel.app portfolio website with AI-powered content management",
    version=settings.app.version,
    debug=settings.app.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
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
