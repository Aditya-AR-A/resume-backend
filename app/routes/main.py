from fastapi import APIRouter, HTTPException
from app.services.data_service import DataService
from app.models.schemas import APIResponse, HealthResponse
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=APIResponse)
async def root():
    """Root endpoint with API information"""
    return APIResponse(
        message="Welcome to Aditya Portfolio Backend API",
        data={
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy")
