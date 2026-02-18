"""
Part 3: Regression Analysis
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from database import mongo_service
from services.analysis import analysis_service
import logging
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)

class RegressionRequest(BaseModel):
    """Request model for multiple regression"""
    predictors: List[str]
    target: str = "body_mass_g"

@router.get("/simple")
async def simple_regression(predictor: str = Query("flipper_length_mm")):
    """Perform simple linear regression"""
    try:
        penguins = mongo_service.get_all_penguins()
        analysis_service.load_data(penguins)
        
        result = analysis_service.simple_regression(predictor)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in /simple: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/multiple")
async def multiple_regression(request: RegressionRequest):
    """Perform multiple linear regression"""
    try:
        penguins = mongo_service.get_all_penguins()
        analysis_service.load_data(penguins)
        
        result = analysis_service.multiple_regression(request.predictors, request.target)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in /multiple: {e}")
        raise HTTPException(status_code=500, detail=str(e))
