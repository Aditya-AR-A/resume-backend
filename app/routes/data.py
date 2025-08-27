from fastapi import APIRouter, HTTPException
from app.services.data_service import DataService
from app.models.schemas import APIResponse

router = APIRouter()


@router.get("/intro", response_model=APIResponse)
async def get_intro():
    """Get introduction data"""
    try:
        data = DataService.get_intro_data()
        return APIResponse(data=data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Intro data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs", response_model=APIResponse)
async def get_jobs():
    """Get work experience/jobs data"""
    try:
        data = DataService.get_jobs_data()
        return APIResponse(data=data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Jobs data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects", response_model=APIResponse)
async def get_projects():
    """Get projects data"""
    try:
        data = DataService.get_projects_data()
        return APIResponse(data=data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Projects data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/new", response_model=APIResponse)
async def get_new_projects():
    """Get new projects data"""
    try:
        data = DataService.get_new_projects_data()
        return APIResponse(data=data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="New projects data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/certificates", response_model=APIResponse)
async def get_certificates():
    """Get certificates data"""
    try:
        data = DataService.get_certificates_data()
        return APIResponse(data=data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Certificates data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layout", response_model=APIResponse)
async def get_layout():
    """Get page layout configuration"""
    try:
        data = DataService.get_layout_data()
        return APIResponse(data=data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Layout data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/page", response_model=APIResponse)
async def get_page_config():
    """Get page configuration"""
    try:
        data = DataService.get_page_data()
        return APIResponse(data=data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Page config not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
