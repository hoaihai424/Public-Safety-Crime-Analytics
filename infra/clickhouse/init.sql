-- Create the main database if it doesn't exist
CREATE DATABASE IF NOT EXISTS crime_data;

-- Use the database
USE crime_data;

-- Create dim date table
CREATE TABLE IF NOT EXISTS dim_date (
    id UUID PRIMARY KEY,
    date TINYINT,
    month TINYINT,
    year SMALLINT,
    quarter TINYINT,
    day_of_week TINYINT,
    is_holiday BOOLEAN,
    is_weekend BOOLEAN
) ENGINE = MergeTree()
 ORDER BY id;


-- Create dim time table
CREATE TABLE IF NOT EXISTS dim_time (
    id UUID PRIMARY KEY,
    hour TINYINT,
    minute TINYINT,
    second TINYINT
) ENGINE = MergeTree()
 ORDER BY id;


-- Create dim primary type table
CREATE TABLE IF NOT EXISTS dim_primary_type (
    id UUID PRIMARY KEY,
    name STRING
) ENGINE = MergeTree()
 ORDER BY id;


-- Create dim crime table
CREATE TABLE IF NOT EXISTS dim_crime (
    id UUID PRIMARY KEY,
    iucr STRING,
    fbi_code STRING,
    primary_type UUID,
    description STRING
) ENGINE = MergeTree()
 ORDER BY id;


-- Create dim location table
CREATE TABLE IF NOT EXISTS dim_location (
    id UUID PRIMARY KEY,
    location STRING,
    latitude FLOAT64,
    longitude FLOAT64,
    block STRING,
    location_description STRING
) ENGINE = MergeTree()
 ORDER BY id;


-- Create dim patrol unit table
CREATE TABLE IF NOT EXISTS dim_patrol_unit (
    id UUID PRIMARY KEY,
    beat STRING,
    district STRING,
    ward STRING,
    community_area STRING
) ENGINE = MergeTree()
 ORDER BY id;


-- Create fact case table
CREATE TABLE IF NOT EXISTS fact_case (
    id UUID PRIMARY KEY,
    case_number STRING,
    arrest_made BOOLEAN,
    domestic BOOLEAN,
    incident_time TIMESTAMP,
    location UUID,
    patrol_unit UUID,
    crime UUID,
    date_id UUID,
    time_id UUID
) ENGINE = MergeTree()
 ORDER BY id;