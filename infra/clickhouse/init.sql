-- Create database
CREATE DATABASE IF NOT EXISTS crime_analytics;

USE crime_analytics;

-- DROP ALL TABLES IF THEY EXIST
DROP TABLE IF EXISTS crime_analytics.dim_date;
DROP TABLE IF EXISTS crime_analytics.dim_time;
DROP TABLE IF EXISTS crime_analytics.dim_primary_type;
DROP TABLE IF EXISTS crime_analytics.dim_crime;
DROP TABLE IF EXISTS crime_analytics.dim_location;
DROP TABLE IF EXISTS crime_analytics.dim_patrol_unit;
DROP TABLE IF EXISTS crime_analytics.fact_case;

-- Date Dimension
CREATE TABLE IF NOT EXISTS crime_analytics.dim_date (
    id String,
    date String,
    month Int8,
    quarter Int8,
    year Int16,
    day_of_week Int8,
    is_weekend Int8
) ENGINE = MergeTree()
ORDER BY id;

-- Time Dimension
CREATE TABLE IF NOT EXISTS crime_analytics.dim_time (
    id String,
    hour Int8,
    minute Int8,
    second Int8
) ENGINE = MergeTree()
ORDER BY id;

-- Primary Type Dimension
CREATE TABLE IF NOT EXISTS crime_analytics.crime_analytics.dim_primary_type (
    id UInt64,
    name String
) ENGINE = MergeTree()
ORDER BY id;

-- Crime Dimension
CREATE TABLE IF NOT EXISTS crime_analytics.dim_crime (
    id Int32,
    iucr String,
    primary_type Int32,
    description String,
    fbi_code String
) ENGINE = MergeTree()
ORDER BY id;

-- Location Dimension
CREATE TABLE IF NOT EXISTS crime_analytics.dim_location (
    id Int32,
    location_description String,
    block String,
    location String
) ENGINE = MergeTree()
ORDER BY id;

-- Patrol Unit Dimension
CREATE TABLE IF NOT EXISTS crime_analytics.dim_patrol_unit (
    id Int32,
    beat Int32,
    district Int32,
    ward Int32,
    community_area Int32
) ENGINE = MergeTree()
ORDER BY id;

-- Case Fact Table
CREATE TABLE IF NOT EXISTS crime_analytics.fact_case (
    id Int32,
    case_number String,
    date_id String,
    time_id String,
    crime_id Int32,
    location_id Int32,
    patrol_unit_id Int32,
    arrest Int8,
    domestic Int8
) ENGINE = MergeTree()
ORDER BY id;


