from fastapi import APIRouter, HTTPException
from app.services.data_service import AIService
from app.models.schemas import (
    APIResponse, AIAnalysisRequest, AIGenerationRequest, AIStatusResponse
)

router = APIRouter()


@router.post("/analyze", response_model=APIResponse)
async def analyze_content(request: AIAnalysisRequest):
    """AI endpoint for content analysis - placeholder"""
    try:
        result = AIService.analyze_content(
            content=request.content,
            analysis_type=request.analysis_type
        )
        return APIResponse(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=APIResponse)
async def generate_content(request: AIGenerationRequest):
    """AI endpoint for content generation - placeholder"""
    try:
        result = AIService.generate_content(
            prompt=request.prompt,
            content_type=request.content_type
        )
        return APIResponse(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status():
    """Get AI system status"""
    try:
        status = AIService.get_ai_status()
        return AIStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
