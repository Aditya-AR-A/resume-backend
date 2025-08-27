from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.services.data_service import DataService
from app.models.schemas import (
    APIResponse, IntroData, JobData, ProjectData, CertificateData,
    LayoutData, PageData, UnifiedSearchResponse, SkillsResponse,
    TimelineResponse, StatsSummary, FilterOptions, PaginatedProjectsResponse,
    PaginatedJobsResponse, PaginatedCertificatesResponse, SearchRequest
)

router = APIRouter()


# ============================================================================
# BASIC DATA ENDPOINTS
# ============================================================================

@router.get("/intro", response_model=APIResponse)
async def get_intro():
    """Get introduction data with proper typing"""
    try:
        data = DataService.get_intro_data()
        return APIResponse(data=data.dict())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Intro data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs", response_model=APIResponse)
async def get_jobs():
    """Get all work experience/jobs data"""
    try:
        data = DataService.get_jobs_data()
        return APIResponse(data=[job.dict() for job in data])
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Jobs data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects", response_model=APIResponse)
async def get_projects():
    """Get all projects data"""
    try:
        data = DataService.get_projects_data()
        return APIResponse(data=[project.dict() for project in data])
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Projects data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/new", response_model=APIResponse)
async def get_new_projects():
    """Get new projects data"""
    try:
        data = DataService.get_new_projects_data()
        return APIResponse(data=[project.dict() for project in data])
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="New projects data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/certificates", response_model=APIResponse)
async def get_certificates():
    """Get all certificates data"""
    try:
        data = DataService.get_certificates_data()
        return APIResponse(data=[cert.dict() for cert in data])
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Certificates data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layout", response_model=APIResponse)
async def get_layout():
    """Get page layout configuration"""
    try:
        data = DataService.get_layout_data()
        return APIResponse(data=data.dict())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Layout data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/page", response_model=APIResponse)
async def get_page_config():
    """Get page configuration"""
    try:
        data = DataService.get_page_data()
        return APIResponse(data=data.dict())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Page config not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# INDIVIDUAL RESOURCE ENDPOINTS
# ============================================================================

@router.get("/projects/{project_id}", response_model=APIResponse)
async def get_project_by_id(project_id: str):
    """Get individual project by ID"""
    try:
        project = DataService.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project with ID '{project_id}' not found")
        return APIResponse(data=project.dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}", response_model=APIResponse)
async def get_job_by_id(job_id: str):
    """Get individual job by ID"""
    try:
        job = DataService.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found")
        return APIResponse(data=job.dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/certificates/{cert_id}", response_model=APIResponse)
async def get_certificate_by_id(cert_id: str):
    """Get individual certificate by ID"""
    try:
        certificate = DataService.get_certificate_by_id(cert_id)
        if not certificate:
            raise HTTPException(status_code=404, detail=f"Certificate with ID '{cert_id}' not found")
        return APIResponse(data=certificate.dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PAGINATED & FILTERED ENDPOINTS
# ============================================================================

@router.get("/projects/paginated", response_model=PaginatedProjectsResponse)
async def get_paginated_projects(
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    skills: Optional[List[str]] = Query(None, description="Filter by skills"),
    featured: Optional[bool] = Query(None, description="Filter by featured status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Get paginated projects with filtering"""
    try:
        filters = FilterOptions(
            skills=skills,
            featured=featured,
            category=category,
            status=status
        )
        return DataService.get_paginated_projects(limit=limit, offset=offset, filters=filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/paginated", response_model=PaginatedJobsResponse)
async def get_paginated_jobs(
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    skills: Optional[List[str]] = Query(None, description="Filter by skills")
):
    """Get paginated jobs with filtering"""
    try:
        filters = FilterOptions(skills=skills)
        return DataService.get_paginated_jobs(limit=limit, offset=offset, filters=filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/certificates/paginated", response_model=PaginatedCertificatesResponse)
async def get_paginated_certificates(
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    skills: Optional[List[str]] = Query(None, description="Filter by skills")
):
    """Get paginated certificates with filtering"""
    try:
        filters = FilterOptions(skills=skills)
        return DataService.get_paginated_certificates(limit=limit, offset=offset, filters=filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UNIFIED SEARCH ENDPOINT
# ============================================================================

@router.get("/search", response_model=UnifiedSearchResponse)
async def unified_search(
    q: str = Query(..., description="Search query"),
    include_sections: List[str] = Query(
        ["projects", "jobs", "certificates"],
        description="Sections to include in search"
    ),
    limit: int = Query(10, ge=1, le=50, description="Maximum results per section")
):
    """Unified search across multiple sections"""
    try:
        return DataService.unified_search(
            query=q,
            include_sections=include_sections,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AGGREGATION ENDPOINTS
# ============================================================================

@router.get("/skills", response_model=SkillsResponse)
async def get_skills_aggregation():
    """Get skills aggregation across all data"""
    try:
        return DataService.get_skills_aggregation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline", response_model=TimelineResponse)
async def get_timeline():
    """Get timeline combining jobs and certificates"""
    try:
        return DataService.get_timeline()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=APIResponse)
async def get_stats_summary():
    """Get portfolio statistics summary"""
    try:
        stats = DataService.get_stats_summary()
        return APIResponse(data=stats.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# LEGACY ENDPOINTS (for backward compatibility)
# ============================================================================

@router.get("/experience", response_model=APIResponse)
async def get_experience():
    """Legacy endpoint for experience data (alias for jobs)"""
    return await get_jobs()


@router.get("/work", response_model=APIResponse)
async def get_work():
    """Legacy endpoint for work data (alias for jobs)"""
    return await get_jobs()
