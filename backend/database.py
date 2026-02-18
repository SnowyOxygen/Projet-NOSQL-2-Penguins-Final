"""
Database connection and query services
"""
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from cassandra.cluster import Cluster
import redis
import json
import logging

from config import settings

logger = logging.getLogger(__name__)

class MongoDBService:
    """MongoDB connection and queries"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(settings.MONGO_URL, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client['penguins']
            self.collection = self.db['penguins']
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
    
    def get_all_penguins(self) -> List[Dict]:
        """Get all penguins"""
        return list(self.collection.find({}, {'_id': 0}))
    
    def get_penguins_by_species(self, species: str) -> List[Dict]:
        """Get penguins by species"""
        return list(self.collection.find({'species': species}, {'_id': 0}))
    
    def enable_sharding(self, shard_key: str = 'species') -> Dict[str, Any]:
        """Enable sharding on the collection with specified shard key"""
        try:
            admin_db = self.client['admin']
            
            # Enable sharding on database
            admin_db.command('enableSharding', 'penguins')
            logger.info("Sharding enabled on 'penguins' database")
            
            # Create shard key index if not exists
            self.collection.create_index(shard_key)
            logger.info(f"Shard key index created on '{shard_key}'")
            
            # Shard the collection
            admin_db.command('shardCollection', 'penguins.penguins', 
                           key={shard_key: 1})
            logger.info(f"Collection sharded with key '{shard_key}'")
            
            return {
                'status': 'success',
                'message': f'Sharding enabled with key: {shard_key}',
                'shard_key': shard_key
            }
        except Exception as e:
            if 'already sharded' in str(e):
                logger.warning(f"Collection already sharded: {e}")
                return {
                    'status': 'already_sharded',
                    'message': 'Collection is already sharded',
                    'error': str(e)
                }
            logger.error(f"Sharding error: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'error': str(e)
            }
    
    def get_sharding_status(self) -> Dict[str, Any]:
        """Get sharding status of the collection"""
        try:
            admin_db = self.client['admin']
            
            # Get collection sharding info
            result = admin_db.command('collStats', 'penguins', count=True)
            
            # Check if sharded
            config_db = self.client['config']
            collections = config_db['collections'].find_one({'_id': 'penguins.penguins'})
            
            if collections:
                return {
                    'is_sharded': True,
                    'shard_key': list(collections.get('key', {}).keys()),
                    'count': result.get('count', 0),
                    'size': result.get('size', 0)
                }
            else:
                return {
                    'is_sharded': False,
                    'count': result.get('count', 0),
                    'size': result.get('size', 0)
                }
        except Exception as e:
            logger.error(f"Error getting sharding status: {e}")
            return {'error': str(e)}
    
    def create_indexes(self) -> Dict[str, str]:
        """Create performance indexes for common queries"""
        try:
            indexes = {}
            
            # Index on species
            self.collection.create_index('species')
            indexes['species'] = 'created'
            
            # Index on island
            self.collection.create_index('island')
            indexes['island'] = 'created'
            
            # Compound index for queries filtering by species and island
            self.collection.create_index([('species', 1), ('island', 1)])
            indexes['species_island'] = 'created'
            
            logger.info(f"Created indexes: {indexes}")
            return indexes
        except Exception as e:
            logger.error(f"Index creation error: {e}")
            return {'error': str(e)}

class CassandraService:
    """Cassandra connection and queries"""
    
    def __init__(self):
        self.cluster = None
        self.session = None
    
    def connect(self):
        """Connect to Cassandra"""
        try:
            self.cluster = Cluster(
                [settings.CASSANDRA_HOST],
                port=settings.CASSANDRA_PORT,
                connect_timeout=10
            )
            self.session = self.cluster.connect('penguins')
            logger.info("Connected to Cassandra")
        except Exception as e:
            logger.error(f"Cassandra connection error: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from Cassandra"""
        if self.session:
            self.session.shutdown()
        if self.cluster:
            self.cluster.shutdown()
    
    def get_all_penguins(self) -> List[Dict]:
        """Get all penguins"""
        rows = self.session.execute('SELECT * FROM penguins')
        return [row._asdict() for row in rows]
    
    def get_penguins_by_species(self, species: str) -> List[Dict]:
        """Get penguins by species"""
        rows = self.session.execute('SELECT * FROM penguins WHERE species = %s', [species])
        return [row._asdict() for row in rows]

class RedisService:
    """Redis connection and queries"""
    
    def __init__(self):
        self.redis = None
    
    def connect(self):
        """Connect to Redis"""
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.redis.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            self.redis.close()
    
    def get_all_penguins(self) -> List[Dict]:
        """Get all penguins from Redis"""
        penguins = []
        for key in self.redis.scan_iter('penguin:*'):
            penguin_data = self.redis.hgetall(key)
            # Convert JSON strings back to Python objects
            penguin = {}
            for k, v in penguin_data.items():
                try:
                    penguin[k] = json.loads(v)
                except:
                    penguin[k] = v
            penguins.append(penguin)
        return penguins

# Global service instances
mongo_service = MongoDBService()
cassandra_service = CassandraService()
redis_service = RedisService()

def init_services():
    """Initialize all database services"""
    mongo_service.connect()
    cassandra_service.connect()
    redis_service.connect()

def close_services():
    """Close all database services"""
    mongo_service.disconnect()
    cassandra_service.disconnect()
    redis_service.disconnect()
