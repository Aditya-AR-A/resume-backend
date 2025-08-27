from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class APIResponse(BaseModel):
    """Base API response model"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    timestamp: datetime = datetime.now()


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = datetime.now()


class IntroData(BaseModel):
    """Introduction data model"""
    name: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    # Add other fields as needed based on your JSON structure


class JobData(BaseModel):
    """Job/Work experience data model"""
    company: Optional[str] = None
    position: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    # Add other fields as needed


class ProjectData(BaseModel):
    """Project data model"""
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    url: Optional[str] = None
    # Add other fields as needed


class CertificateData(BaseModel):
    """Certificate data model"""
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None
    # Add other fields as needed


class LayoutData(BaseModel):
    """Layout configuration model"""
    sections: Optional[List[str]] = None
    # Add other fields as needed


class PageData(BaseModel):
    """Page configuration model"""
    title: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    # Add other fields as needed


# AI System Models (for future implementation)
class AIAnalysisRequest(BaseModel):
    """AI analysis request model"""
    content: str
    analysis_type: Optional[str] = "general"


class AIGenerationRequest(BaseModel):
    """AI content generation request model"""
    prompt: str
    content_type: Optional[str] = "text"


class AIStatusResponse(BaseModel):
    """AI system status response"""
    status: str
    components: Dict[str, str]
    timestamp: datetime = datetime.now()
