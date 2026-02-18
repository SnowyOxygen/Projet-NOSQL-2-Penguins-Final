"""
Part 5: Database Benchmarking
"""
from fastapi import APIRouter, HTTPException
import time
import logging
from datetime import datetime
from typing import Dict, List, Any

from database import mongo_service, cassandra_service, redis_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Configuration for benchmarking
BENCHMARK_QUERIES = 10  # Number of queries per database
QUERY_BATCH_SIZE = 5    # Number of pagination queries


class BenchmarkResult:
    """Class to store benchmark results"""
    def __init__(self):
        self.times: List[float] = []
        self.total_time: float = 0
        self.min_time: float = float('inf')
        self.max_time: float = 0
        self.total_queries: int = 0

    def add_time(self, time_ms: float):
        """Add a query time measurement"""
        self.times.append(time_ms)
        self.total_time += time_ms
        self.min_time = min(self.min_time, time_ms)
        self.max_time = max(self.max_time, time_ms)
        self.total_queries += 1

    def get_summary(self) -> Dict[str, float]:
        """Get summary statistics"""
        if self.total_queries == 0:
            return {
                'avg_time': 0,
                'min_time': 0,
                'max_time': 0,
                'throughput': 0,
                'total_queries': 0
            }
        
        avg_time = self.total_time / self.total_queries
        throughput = 1000.0 / avg_time if avg_time > 0 else 0  # ops per second
        
        return {
            'avg_time': avg_time,
            'min_time': self.min_time,
            'max_time': self.max_time,
            'throughput': throughput,
            'total_queries': self.total_queries
        }


def benchmark_mongodb() -> tuple[BenchmarkResult, List[Dict[str, float]]]:
    """Benchmark MongoDB"""
    result = BenchmarkResult()
    detailed = []
    
    try:
        # Test 1: Get all penguins
        for _ in range(BENCHMARK_QUERIES):
            start = time.time()
            penguins = mongo_service.get_all_penguins()
            end = time.time()
            time_ms = (end - start) * 1000
            result.add_time(time_ms)
            detailed.append({'time': time_ms, 'operation': 'get_all'})
        
        # Test 2: Get by species
        species_list = ['Adelie', 'Chinstrap', 'Gentoo']
        for species in species_list:
            for _ in range(QUERY_BATCH_SIZE):
                start = time.time()
                penguins = mongo_service.get_penguins_by_species(species)
                end = time.time()
                time_ms = (end - start) * 1000
                result.add_time(time_ms)
                detailed.append({'time': time_ms, 'operation': f'get_by_species_{species}'})
        
        logger.info(f"MongoDB benchmark completed: {result.total_queries} queries")
    except Exception as e:
        logger.error(f"MongoDB benchmark error: {e}")
        raise
    
    return result, detailed


def benchmark_cassandra() -> tuple[BenchmarkResult, List[Dict[str, float]]]:
    """Benchmark Cassandra"""
    result = BenchmarkResult()
    detailed = []
    
    try:
        # Test 1: Get all penguins
        for _ in range(BENCHMARK_QUERIES):
            start = time.time()
            penguins = cassandra_service.get_all_penguins()
            end = time.time()
            time_ms = (end - start) * 1000
            result.add_time(time_ms)
            detailed.append({'time': time_ms, 'operation': 'get_all'})
        
        # Test 2: Get by species
        species_list = ['Adelie', 'Chinstrap', 'Gentoo']
        for species in species_list:
            for _ in range(QUERY_BATCH_SIZE):
                start = time.time()
                penguins = cassandra_service.get_penguins_by_species(species)
                end = time.time()
                time_ms = (end - start) * 1000
                result.add_time(time_ms)
                detailed.append({'time': time_ms, 'operation': f'get_by_species_{species}'})
        
        logger.info(f"Cassandra benchmark completed: {result.total_queries} queries")
    except Exception as e:
        logger.error(f"Cassandra benchmark error: {e}")
        raise
    
    return result, detailed


def benchmark_redis() -> tuple[BenchmarkResult, List[Dict[str, float]]]:
    """Benchmark Redis"""
    result = BenchmarkResult()
    detailed = []
    
    try:
        # Test 1: Get all penguins
        for _ in range(BENCHMARK_QUERIES):
            start = time.time()
            penguins = redis_service.get_all_penguins()
            end = time.time()
            time_ms = (end - start) * 1000
            result.add_time(time_ms)
            detailed.append({'time': time_ms, 'operation': 'get_all'})
        
        # Test 2: Get all and filter (simulating by species)
        species_list = ['Adelie', 'Chinstrap', 'Gentoo']
        for species in species_list:
            for _ in range(QUERY_BATCH_SIZE):
                start = time.time()
                all_penguins = redis_service.get_all_penguins()
                # Filter in memory
                filtered = [p for p in all_penguins if p.get('species') == species]
                end = time.time()
                time_ms = (end - start) * 1000
                result.add_time(time_ms)
                detailed.append({'time': time_ms, 'operation': f'get_by_species_{species}'})
        
        logger.info(f"Redis benchmark completed: {result.total_queries} queries")
    except Exception as e:
        logger.error(f"Redis benchmark error: {e}")
        raise
    
    return result, detailed


@router.post("/mongodb")
async def benchmark_single_mongodb():
    """Run benchmark for MongoDB only"""
    try:
        result, detailed = benchmark_mongodb()
        return {
            "database": "MongoDB",
            "metrics": result.get_summary(),
            "detailed_results": detailed,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Benchmark error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cassandra")
async def benchmark_single_cassandra():
    """Run benchmark for Cassandra only"""
    try:
        result, detailed = benchmark_cassandra()
        return {
            "database": "Cassandra",
            "metrics": result.get_summary(),
            "detailed_results": detailed,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Benchmark error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/redis")
async def benchmark_single_redis():
    """Run benchmark for Redis only"""
    try:
        result, detailed = benchmark_redis()
        return {
            "database": "Redis",
            "metrics": result.get_summary(),
            "detailed_results": detailed,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Benchmark error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/all")
async def benchmark_all_databases():
    """Run benchmark for all databases"""
    benchmark_start = time.time()
    
    try:
        # Run benchmarks for all three databases
        mongo_result, mongo_detailed = benchmark_mongodb()
        cassandra_result, cassandra_detailed = benchmark_cassandra()
        redis_result, redis_detailed = benchmark_redis()
        
        benchmark_end = time.time()
        total_duration = benchmark_end - benchmark_start
        
        return {
            "benchmarks": {
                "mongodb": mongo_result.get_summary(),
                "cassandra": cassandra_result.get_summary(),
                "redis": redis_result.get_summary()
            },
            "detailed_results": {
                "mongodb": mongo_detailed,
                "cassandra": cassandra_detailed,
                "redis": redis_detailed
            },
            "total_duration": total_duration,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Benchmark error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_benchmark_info():
    """Get benchmark configuration information"""
    return {
        "benchmark_queries": BENCHMARK_QUERIES,
        "query_batch_size": QUERY_BATCH_SIZE,
        "total_queries_per_db": BENCHMARK_QUERIES + (3 * QUERY_BATCH_SIZE),
        "description": "Database benchmarking compares query performance across MongoDB, Cassandra, and Redis"
    }


def benchmark_mongodb_detailed(label: str = "benchmark") -> tuple[BenchmarkResult, List[Dict[str, float]]]:
    """Benchmark MongoDB with detailed operation tracking"""
    result = BenchmarkResult()
    detailed = []
    
    try:
        # Test 1: Get all penguins (10 queries)
        for i in range(BENCHMARK_QUERIES):
            start = time.time()
            penguins = mongo_service.get_all_penguins()
            end = time.time()
            time_ms = (end - start) * 1000
            result.add_time(time_ms)
            detailed.append({
                'time': time_ms,
                'operation': 'get_all',
                'query_num': i + 1,
                'label': label
            })
        
        # Test 2: Get by species (5 queries per species)
        species_list = ['Adelie', 'Chinstrap', 'Gentoo']
        for species in species_list:
            for i in range(QUERY_BATCH_SIZE):
                start = time.time()
                penguins = mongo_service.get_penguins_by_species(species)
                end = time.time()
                time_ms = (end - start) * 1000
                result.add_time(time_ms)
                detailed.append({
                    'time': time_ms,
                    'operation': f'get_by_species_{species}',
                    'query_num': i + 1,
                    'label': label
                })
        
        logger.info(f"MongoDB {label} benchmark completed: {result.total_queries} queries")
    except Exception as e:
        logger.error(f"MongoDB {label} benchmark error: {e}")
        raise
    
    return result, detailed


@router.post("/sharding/before")
async def benchmark_before_sharding():
    """Benchmark MongoDB BEFORE sharding is enabled"""
    try:
        # Ensure indexes exist
        mongo_service.create_indexes()
        
        # Run benchmark before sharding
        result, detailed = benchmark_mongodb_detailed("before_sharding")
        summary = result.get_summary()
        
        return {
            "phase": "before_sharding",
            "description": "Benchmark without sharding enabled - single node operation",
            "metrics": summary,
            "detailed_results": detailed,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Benchmark error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sharding/enable")
async def enable_mongodb_sharding():
    """Enable sharding on MongoDB collection"""
    try:
        sharding_result = mongo_service.enable_sharding(shard_key='species')
        sharding_status = mongo_service.get_sharding_status()
        
        return {
            "action": "enable_sharding",
            "sharding_result": sharding_result,
            "sharding_status": sharding_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Sharding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sharding/after")
async def benchmark_after_sharding():
    """Benchmark MongoDB AFTER sharding is enabled"""
    try:
        # Run benchmark after sharding
        result, detailed = benchmark_mongodb_detailed("after_sharding")
        summary = result.get_summary()
        sharding_status = mongo_service.get_sharding_status()
        
        return {
            "phase": "after_sharding",
            "description": "Benchmark with sharding enabled - distributed operation",
            "metrics": summary,
            "sharding_status": sharding_status,
            "detailed_results": detailed,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Benchmark error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sharding/comparison")
async def sharding_comparison():
    """Run complete sharding comparison: before -> enable -> after"""
    try:
        # Phase 1: Benchmark before sharding
        mongo_service.create_indexes()
        before_result, before_detailed = benchmark_mongodb_detailed("before_sharding")
        before_summary = before_result.get_summary()
        
        # Phase 2: Enable sharding
        sharding_result = mongo_service.enable_sharding(shard_key='species')
        
        # Wait a moment for sharding to stabilize
        time.sleep(1)
        
        # Phase 3: Benchmark after sharding
        after_result, after_detailed = benchmark_mongodb_detailed("after_sharding")
        after_summary = after_result.get_summary()
        
        # Calculate improvements
        improvement = {}
        if before_summary['avg_time'] > 0:
            improvement['avg_time_improvement'] = (
                (before_summary['avg_time'] - after_summary['avg_time']) / 
                before_summary['avg_time'] * 100
            )
            improvement['throughput_improvement'] = (
                (after_summary['throughput'] - before_summary['throughput']) / 
                before_summary['throughput'] * 100 if before_summary['throughput'] > 0 else 0
            )
        
        return {
            "comparison": {
                "before_sharding": {
                    "description": "Single node operation without sharding",
                    "metrics": before_summary,
                    "queries": len(before_detailed)
                },
                "sharding_action": sharding_result,
                "after_sharding": {
                    "description": "Distributed operation with sharding on 'species' key",
                    "metrics": after_summary,
                    "queries": len(after_detailed)
                }
            },
            "improvement_metrics": {
                "avg_time_improvement_percent": improvement.get('avg_time_improvement', 0),
                "throughput_improvement_percent": improvement.get('throughput_improvement', 0),
                "note": "Positive improvement % means after sharding is faster"
            },
            "comparison_table": {
                "metric": ["Avg Time (ms)", "Min Time (ms)", "Max Time (ms)", "Throughput (req/s)"],
                "before": [
                    round(before_summary['avg_time'], 2),
                    round(before_summary['min_time'], 2),
                    round(before_summary['max_time'], 2),
                    round(before_summary['throughput'], 2)
                ],
                "after": [
                    round(after_summary['avg_time'], 2),
                    round(after_summary['min_time'], 2),
                    round(after_summary['max_time'], 2),
                    round(after_summary['throughput'], 2)
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Sharding comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
