// MongoDB initialization script
db = db.getSiblingDB('penguins');

// Create collection with schema validation
// CSV data will be loaded via Python init.py script
db.createCollection('penguins', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['studyName', 'sampleNumber', 'species', 'island'],
      properties: {
        studyName: { bsonType: 'string' },
        sampleNumber: { bsonType: 'int' },
        species: { bsonType: 'string' },
        region: { bsonType: 'string' },
        island: { bsonType: 'string' },
        stage: { bsonType: 'string' },
        individualId: { bsonType: 'string' },
        clutchCompletion: { bsonType: 'string' },
        dateEgg: { bsonType: 'string' },
        culmenLength: { bsonType: ['double', 'null'] },
        culmenDepth: { bsonType: ['double', 'null'] },
        flipperLength: { bsonType: ['int', 'null'] },
        bodyMass: { bsonType: ['int', 'null'] },
        sex: { bsonType: ['string', 'null'] },
        delta15N: { bsonType: ['double', 'null'] },
        delta13C: { bsonType: ['double', 'null'] },
        comments: { bsonType: ['string', 'null'] }
      }
    }
  }
});

// Create indexes for performance optimization
db.penguins.createIndex({ species: 1 });
db.penguins.createIndex({ island: 1 });
db.penguins.createIndex({ sex: 1 });
db.penguins.createIndex({ species: 1, island: 1 });

print('MongoDB penguins collection created with indexes');

// Note: Sharding is configured via API endpoints in backend/routers/part5.py
// To enable sharding, use the /api/benchmark/sharding/enable endpoint after data is loaded
// This requires MongoDB to be deployed as a sharded cluster (see docker-compose-sharded.yml)
print('Sharding can be enabled via API after migration to sharded cluster setup');
