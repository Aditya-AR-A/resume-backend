from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.ai_service import ai_service
from app.models.schemas import (
    APIResponse, AIRequest, AIResponse, SearchRequest, SearchResult,
    QuestionAnsweringRequest, QuestionAnsweringResponse, AIStatusResponse,
    MessageClassification, LLMProvider
)

router = APIRouter()


# ============================================================================
# LLM AGENT ENDPOINTS
# ============================================================================

@router.post("/chat", response_model=AIResponse)
async def chat_with_ai(request: AIRequest):
    """Enhanced AI chat endpoint with LLM agent processing"""
    try:
        response = await ai_service.process_request(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")


@router.post("/ask", response_model=QuestionAnsweringResponse)
async def answer_question(request: QuestionAnsweringRequest):
    """Question answering endpoint using LLM agent"""
    try:
        # Convert to AIRequest format
        ai_request = AIRequest(
            message=request.question,
            context=request.context,
            metadata={"domain": request.domain}
        )

        # Process through LLM agent
        ai_response = await ai_service.process_request(ai_request)

        # Convert to QuestionAnsweringResponse format
        return QuestionAnsweringResponse(
            answer=ai_response.response,
            confidence=ai_response.confidence,
            sources=ai_response.sources or [],
            related_questions=ai_response.suggestions,
            processing_time=ai_response.processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question answering error: {str(e)}")


# ============================================================================
# MESSAGE CLASSIFICATION ENDPOINTS
# ============================================================================

@router.post("/classify", response_model=APIResponse)
async def classify_message(request: AIRequest):
    """Endpoint to classify a message without full LLM processing"""
    try:
        classification = ai_service.classifier.classify_message(request.message)
        return APIResponse(data=classification.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")


# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@router.post("/search", response_model=SearchResult)
async def search_content(request: SearchRequest):
    """Search endpoint with enhanced filtering and LLM-powered semantic search"""
    try:
        return await ai_service.semantic_search(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


# ============================================================================
# CONTENT ANALYSIS & GENERATION ENDPOINTS
# ============================================================================

@router.post("/analyze", response_model=APIResponse)
async def analyze_content(request: AIRequest):
    """AI endpoint for content analysis with message classification"""
    try:
        # Classify the message first
        classification = ai_service.classifier.classify_message(request.message)

        # Create analysis request for LLM
        analysis_request = AIRequest(
            message=f"Please analyze the following content: {request.message}",
            context=request.context,
            metadata={"analysis_type": "content_analysis"}
        )

        # Process through LLM agent
        analysis_response = await ai_service.process_request(analysis_request)

        analysis_result = {
            "classification": classification.dict(),
            "llm_analysis": analysis_response.response,
            "confidence": analysis_response.confidence,
            "processing_time": analysis_response.processing_time,
            "provider": analysis_response.provider.value if analysis_response.provider else None,
            "model": analysis_response.model
        }

        return APIResponse(data=analysis_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.post("/generate", response_model=APIResponse)
async def generate_content(request: AIRequest):
    """AI endpoint for content generation with context awareness"""
    try:
        # Process through LLM agent
        response = await ai_service.process_request(request)
        return APIResponse(data=response.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")


# ============================================================================
# SYSTEM STATUS & MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status():
    """Get comprehensive AI system status"""
    try:
        return ai_service.get_ai_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check error: {str(e)}")


@router.get("/providers", response_model=APIResponse)
async def get_available_providers():
    """Get list of available LLM providers"""
    try:
        providers = ai_service.agent.provider_manager.get_available_providers()
        provider_info = []

        for provider in providers:
            config = ai_service.agent.provider_manager.providers[provider].config
            provider_info.append({
                "provider": provider.value,
                "model": config.model,
                "available": True
            })

        return APIResponse(data={
            "providers": provider_info,
            "total_available": len(provider_info)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Provider check error: {str(e)}")


# ============================================================================
# SPECIALIZED AI ENDPOINTS
# ============================================================================

@router.post("/summarize", response_model=APIResponse)
async def summarize_content(request: AIRequest):
    """Summarize content using LLM agent"""
    try:
        summary_request = AIRequest(
            message=f"Please provide a concise summary of: {request.message}",
            context=request.context,
            metadata={"task": "summarization"}
        )

        response = await ai_service.process_request(summary_request)
        return APIResponse(data={
            "summary": response.response,
            "confidence": response.confidence,
            "processing_time": response.processing_time,
            "provider": response.provider.value if response.provider else None
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")


@router.post("/extract-keywords", response_model=APIResponse)
async def extract_keywords(request: AIRequest):
    """Extract keywords from content using LLM and classification"""
    try:
        # Get classification keywords
        classification = ai_service.classifier.classify_message(request.message)

        # Use LLM for additional keyword extraction
        keyword_request = AIRequest(
            message=f"Extract the most important keywords and phrases from: {request.message}",
            context=request.context,
            metadata={"task": "keyword_extraction"}
        )

        llm_response = await ai_service.process_request(keyword_request)

        return APIResponse(data={
            "classification_keywords": classification.keywords,
            "llm_keywords": llm_response.response,
            "confidence": (classification.confidence + llm_response.confidence) / 2,
            "processing_time": classification.processing_time + llm_response.processing_time
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword extraction error: {str(e)}")


# ============================================================================
# LEGACY ENDPOINTS (for backward compatibility)
# ============================================================================

@router.post("/query", response_model=AIResponse)
async def legacy_query_endpoint(request: AIRequest):
    """Legacy query endpoint (alias for /chat)"""
    return await chat_with_ai(request)


@router.get("/health", response_model=APIResponse)
async def ai_health_check():
    """AI system health check"""
    try:
        status = ai_service.get_ai_status()
        return APIResponse(data={
            "status": "healthy" if status.components.get("llm_agent") == "active" else "unhealthy",
            "components": status.components,
            "providers": status.providers
        })
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"AI health check failed: {str(e)}",
            data={"status": "unhealthy"}
        )
