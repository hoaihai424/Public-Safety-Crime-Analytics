-- Create a keyspace for the crime data
CREATE KEYSPACE IF NOT EXISTS crime_data WITH REPLICATION = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

-- Use the new keyspace
USE crime_data;

-- Create a table to hold the raw crime incidents
CREATE TABLE IF NOT EXISTS crime_incidents (
    incident_id UUID PRIMARY KEY,
    report_date TIMESTAMP,
    crime_type TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    latitude DOUBLE,
    longitude DOUBLE,
    -- Add other relevant fields from your CSV
    raw_data TEXT,
    created_at TIMESTAMP
);
