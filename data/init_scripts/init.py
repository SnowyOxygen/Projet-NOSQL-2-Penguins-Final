"""
Database initialization script - loads CSV data into MongoDB, Cassandra, and Redis
"""
import csv
import json
import time
import os
from typing import List, Dict, Any

# MongoDB
from pymongo import MongoClient, ASCENDING

# Cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Redis
import redis

def parse_csv(filepath: str) -> List[Dict[str, Any]]:
    """Parse the penguins CSV file into a list of dictionaries"""
    penguins = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean up the data
            penguin = {
                'studyName': row['studyName'],
                'sampleNumber': int(row['Sample Number']) if row['Sample Number'] else None,
                'species': row['Species'].replace(' Penguin (Pygoscelis ', '').replace('adeliae)', 'Adelie').replace('antarctica)', 'Chinstrap').replace('papua)', 'Gentoo').split()[0],
                'region': row['Region'],
                'island': row['Island'],
                'stage': row['Stage'],
                'individualId': row['Individual ID'],
                'clutchCompletion': row['Clutch Completion'],
                'dateEgg': row['Date Egg'],
                'culmenLength': float(row['Culmen Length (mm)']) if row['Culmen Length (mm)'] else None,
                'culmenDepth': float(row['Culmen Depth (mm)']) if row['Culmen Depth (mm)'] else None,
                'flipperLength': int(row['Flipper Length (mm)']) if row['Flipper Length (mm)'] else None,
                'bodyMass': int(row['Body Mass (g)']) if row['Body Mass (g)'] else None,
                'sex': row['Sex'] if row['Sex'] else None,
                'delta15N': float(row['Delta 15 N (o/oo)']) if row['Delta 15 N (o/oo)'] else None,
                'delta13C': float(row['Delta 13 C (o/oo)']) if row['Delta 13 C (o/oo)'] else None,
                'comments': row['Comments'] if row['Comments'] else None
            }
            penguins.append(penguin)
    return penguins

def init_mongodb(penguins: List[Dict], host: str = 'mongodb', port: int = 27017):
    """Initialize MongoDB with penguins data"""
    print(f"[MongoDB] Connecting to {host}:{port}...")
    try:
        client = MongoClient(f'mongodb://{host}:{port}/', serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client['penguins']
        collection = db['penguins']
        
        # Drop existing data
        collection.drop()
        
        # Insert data
        result = collection.insert_many(penguins)
        print(f"[MongoDB] Inserted {len(result.inserted_ids)} penguin records")
        
        # Create indexes
        collection.create_index([('species', ASCENDING)])
        collection.create_index([('island', ASCENDING)])
        collection.create_index([('sex', ASCENDING)])
        print("[MongoDB] Indexes created")
        
        client.close()
    except Exception as e:
        print(f"[MongoDB] Error: {e}")

def init_cassandra(penguins: List[Dict], host: str = 'cassandra', port: int = 9042):
    """Initialize Cassandra with penguins data"""
    print(f"[Cassandra] Connecting to {host}:{port}...")
    try:
        cluster = Cluster([host], port=port, connect_timeout=10)
        session = cluster.connect()
        
        # Create keyspace
        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS penguins
            WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """)
        
        session.set_keyspace('penguins')
        
        # Create table
        session.execute("""
            CREATE TABLE IF NOT EXISTS penguins (
                study_name TEXT,
                sample_number INT,
                species TEXT,
                region TEXT,
                island TEXT,
                stage TEXT,
                individual_id TEXT,
                clutch_completion TEXT,
                date_egg TEXT,
                culmen_length_mm DOUBLE,
                culmen_depth_mm DOUBLE,
                flipper_length_mm INT,
                body_mass_g INT,
                sex TEXT,
                delta_15_n DOUBLE,
                delta_13_c DOUBLE,
                comments TEXT,
                PRIMARY KEY ((species), sample_number)
            ) WITH CLUSTERING ORDER BY (sample_number ASC)
        """)
        
        # Insert data
        insert_stmt = session.prepare("""
            INSERT INTO penguins (
                study_name, sample_number, species, region, island, stage,
                individual_id, clutch_completion, date_egg, culmen_length_mm,
                culmen_depth_mm, flipper_length_mm, body_mass_g, sex,
                delta_15_n, delta_13_c, comments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """)
        
        for penguin in penguins:
            session.execute(insert_stmt, (
                penguin['studyName'],
                penguin['sampleNumber'],
                penguin['species'],
                penguin['region'],
                penguin['island'],
                penguin['stage'],
                penguin['individualId'],
                penguin['clutchCompletion'],
                penguin['dateEgg'],
                penguin['culmenLength'],
                penguin['culmenDepth'],
                penguin['flipperLength'],
                penguin['bodyMass'],
                penguin['sex'],
                penguin['delta15N'],
                penguin['delta13C'],
                penguin['comments']
            ))
        
        print(f"[Cassandra] Inserted {len(penguins)} penguin records")
        cluster.shutdown()
    except Exception as e:
        print(f"[Cassandra] Error: {e}")

def init_redis(penguins: List[Dict], host: str = 'redis', port: int = 6379):
    """Initialize Redis with penguins data"""
    print(f"[Redis] Connecting to {host}:{port}...")
    try:
        r = redis.Redis(host=host, port=port, decode_responses=True, socket_connect_timeout=5)
        r.ping()
        
        # Store each penguin as a hash
        for penguin in penguins:
            # Remove MongoDB ObjectId before serialization
            penguin_data = {k: v for k, v in penguin.items() if k != '_id'}
            key = f"penguin:{penguin_data['sampleNumber']}"
            r.hset(key, mapping={k: json.dumps(v) if v is not None else 'null' for k, v in penguin_data.items()})
            
            # Add to species set
            species = penguin['species']
            r.sadd(f"species:{species}", penguin['sampleNumber'])
            
            # Add to island set
            island = penguin['island']
            r.sadd(f"island:{island}", penguin['sampleNumber'])
        
        print(f"[Redis] Stored {len(penguins)} penguin records")
        r.close()
    except Exception as e:
        print(f"[Redis] Error: {e}")

def main():
    """Main initialization function"""
    print("=" * 60)
    print("Penguins Database Initialization")
    print("=" * 60)
    
    # Get environment variables
    mongo_host = os.getenv('MONGO_HOST', 'mongodb')
    cassandra_host = os.getenv('CASSANDRA_HOST', 'cassandra')
    redis_host = os.getenv('REDIS_HOST', 'redis')
    csv_path = '/app/penguins_lter.csv'
    
    # Wait for services to be ready
    print("\nWaiting for databases to be ready...")
    time.sleep(5)
    
    # Parse CSV
    print(f"\nParsing CSV from {csv_path}...")
    penguins = parse_csv(csv_path)
    print(f"✓ Parsed {len(penguins)} penguin records")
    
    # Initialize databases
    print("\nInitializing databases...")
    init_mongodb(penguins, host=mongo_host)
    init_cassandra(penguins, host=cassandra_host)
    init_redis(penguins, host=redis_host)
    
    print("\n" + "=" * 60)
    print("Initialization complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
