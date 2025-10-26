-- Create a keyspace for the crime data
CREATE KEYSPACE IF NOT EXISTS crime_data WITH REPLICATION = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

-- Use the new keyspace
USE crime_data;

-- Create primary type table
CREATE TABLE IF NOT EXISTS primary_type (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    name TEXT
);

-- Create crime table
CREATE TABLE IF NOT EXISTS crime (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    iucr TEXT,
    fbi_code TEXT,
    primary_type UUID,
    description TEXT
);

-- Create location table
CREATE TABLE IF NOT EXISTS location (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    location TEXT,
    latitude DOUBLE,
    longitude DOUBLE,
    block TEXT,
    location_description TEXT
);

-- Create patrol unit table
CREATE TABLE IF NOT EXISTS patrol_unit (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    beat TEXT,
    district TEXT,
    ward TEXT,
    community_area TEXT
);

-- Create case table
CREATE TABLE IF NOT EXISTS case (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    case_number TEXT,
    arrest_made BOOLEAN,
    domestic BOOLEAN,
    incident_time TIMESTAMP,
    location UUID,
    patrol_unit UUID,
    crime UUID
);