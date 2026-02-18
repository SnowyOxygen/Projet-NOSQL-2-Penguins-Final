"""
Health check router
"""
from fastapi import APIRouter, HTTPException
from database import mongo_service, cassandra_service, redis_service

router = APIRouter()

@router.get("")
async def health_check():
    """Check database connections"""
    status = {
        "mongodb": "disconnected",
        "cassandra": "disconnected",
        "redis": "disconnected"
    }
    
    # Check MongoDB
    try:
        mongo_service.client.admin.command('ping')
        status["mongodb"] = "connected"
    except:
        status["mongodb"] = "disconnected"
    
    # Check Cassandra
    try:
        cassandra_service.session.execute('SELECT 1')
        status["cassandra"] = "connected"
    except:
        status["cassandra"] = "disconnected"
    
    # Check Redis
    try:
        redis_service.redis.ping()
        status["redis"] = "connected"
    except:
        status["redis"] = "disconnected"
    
    all_ok = all(v == "connected" for v in status.values())
    
    return {
        "status": "healthy" if all_ok else "degraded",
        "databases": status
    }
