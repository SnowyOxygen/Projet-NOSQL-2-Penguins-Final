"""
Part 1: Descriptive Statistical Analysis
"""
from fastapi import APIRouter, HTTPException
from database import mongo_service
from services.analysis import analysis_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/summary")
async def get_summary():
    """Get descriptive statistics summary"""
    try:
        # Fetch data from MongoDB
        penguins = mongo_service.get_all_penguins()
        if not penguins:
            raise HTTPException(status_code=404, detail="No penguin data found")
        
        # Load data into analysis service
        analysis_service.load_data(penguins)
        
        # Get summary
        summary = analysis_service.get_part1_summary()
        return summary
    except Exception as e:
        logger.error(f"Error in /summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/numeric-stats")
async def get_numeric_stats():
    """Get statistics for numeric variables"""
    try:
        penguins = mongo_service.get_all_penguins()
        analysis_service.load_data(penguins)
        summary = analysis_service.get_part1_summary()
        return {"numeric_stats": summary["numeric_stats"]}
    except Exception as e:
        logger.error(f"Error in /numeric-stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/species")
async def get_species_distribution():
    """Get species distribution"""
    try:
        penguins = mongo_service.get_all_penguins()
        analysis_service.load_data(penguins)
        summary = analysis_service.get_part1_summary()
        return {"species_counts": summary["species_counts"]}
    except Exception as e:
        logger.error(f"Error in /species: {e}")
        raise HTTPException(status_code=500, detail=str(e))
