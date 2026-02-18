-- Cassandra CQL initialization script
-- This will be executed by the Python init script

CREATE KEYSPACE IF NOT EXISTS penguins
  WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
  };

USE penguins;

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
) WITH CLUSTERING ORDER BY (sample_number ASC);

CREATE INDEX ON penguins (island);
CREATE INDEX ON penguins (sex);
CREATE INDEX ON penguins (region);

-- Trigger to get all penguins
CREATE TABLE IF NOT EXISTS penguins_by_island (
  island TEXT,
  species TEXT,
  sample_number INT,
  study_name TEXT,
  individual_id TEXT,
  body_mass_g INT,
  culmen_length_mm DOUBLE,
  culmen_depth_mm DOUBLE,
  flipper_length_mm INT,
  sex TEXT,
  PRIMARY KEY ((island), species, sample_number)
);
