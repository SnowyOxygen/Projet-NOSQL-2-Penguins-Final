"""
FastAPI application for Penguins Analysis
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from config import settings
from routers import part1, part2, part3, part4, part5, health
from database import init_services, close_services

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Penguins Analysis API",
    description="API for multi-database penguin species classification and analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lifecycle events
@app.on_event("startup")
async def startup():
    """Initialize database connections on startup"""
    try:
        init_services()
        logger.info("Database services initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database services: {e}")

@app.on_event("shutdown")
async def shutdown():
    """Close database connections on shutdown"""
    close_services()
    logger.info("Database services closed")

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(part1.router, prefix="/api/part1", tags=["part1_statistics"])
app.include_router(part2.router, prefix="/api/part2", tags=["part2_visualization"])
app.include_router(part3.router, prefix="/api/part3", tags=["part3_regression"])
app.include_router(part4.router, prefix="/api/part4", tags=["part4_classification"])
app.include_router(part5.router, prefix="/api/benchmark", tags=["benchmark"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Penguins Analysis API",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
