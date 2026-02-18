"""
Part 2: Data Visualization
"""
from fastapi import APIRouter, HTTPException, Query
from database import mongo_service
from services.analysis import analysis_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/distribution")
async def get_distribution(variable: str = Query("body_mass_g")):
    """Get distribution data for a variable"""
    try:
        penguins = mongo_service.get_all_penguins()
        analysis_service.load_data(penguins)
        
        distribution = analysis_service.get_distribution_data(variable)
        return distribution
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in /distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/correlation")
async def get_correlation():
    """Get correlation matrix"""
    try:
        penguins = mongo_service.get_all_penguins()
        analysis_service.load_data(penguins)
        
        correlation = analysis_service.get_correlation_matrix()
        return correlation
    except Exception as e:
        logger.error(f"Error in /correlation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scatter")
async def get_scatter_data():
    """Get scatter plot data for relationship analysis"""
    try:
        penguins = mongo_service.get_all_penguins()
        analysis_service.load_data(penguins)
        
        scatter = analysis_service.get_scatter_data()
        return scatter
    except Exception as e:
        logger.error(f"Error in /scatter: {e}")
        raise HTTPException(status_code=500, detail=str(e))
