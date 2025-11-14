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
CREATE TABLE crime_analytics.dim_date (
    id String,
    date Date,
    month UInt8,
    quarter UInt8,
    year UInt16,
    day_of_week String,
    is_weekend UInt8
) ENGINE = MergeTree()
ORDER BY (year, month, date)
PARTITION BY toYYYYMM(date);

ALTER TABLE crime_analytics.dim_date ADD INDEX idx_date (id) TYPE minmax GRANULARITY 1;

-- Time Dimension
CREATE TABLE IF NOT EXISTS crime_analytics.dim_time (
    id String,
    hour UInt8,
    minute UInt8,
    second UInt8
) ENGINE = MergeTree()
ORDER BY (hour, minute, second);

-- Time Dimension (00:00:00 to 23:59:00, only HH:MM:00)
CREATE TABLE crime_analytics.dim_time (
    id String,                    -- Format: HHMM00 (e.g., "143000" for 14:30:00)
    hour UInt8,                   -- 0-23
    minute UInt8,                 -- 0-59
    second UInt8                  -- Always 0 (seconds rounded to 0)
) ENGINE = MergeTree()
ORDER BY (hour, minute)

-- Primary Type Dimension
CREATE TABLE IF NOT EXISTS crime_analytics.dim_primary_type (
    id UInt64,
    name String
) ENGINE = MergeTree()
ORDER BY id;

-- Crime Dimension
CREATE TABLE IF NOT EXISTS crime_analytics.dim_crime (
    id UInt64,
    iucr String,
    primary_type UInt64,
    description String,
    fbi_code String
) ENGINE = MergeTree()
ORDER BY id;

-- Location Dimension
CREATE TABLE IF NOT EXISTS crime_analytics.dim_location (
    id UInt64,
    location_description String,
    block String,
    latitude Float64,
    longitude Float64,
    location String
) ENGINE = MergeTree()
ORDER BY id;

-- Patrol Unit Dimension
CREATE TABLE IF NOT EXISTS crime_analytics.dim_patrol_unit (
    id UInt64,
    beat Int32,
    district Int32,
    ward Int32,
    community_area Int32
) ENGINE = MergeTree()
ORDER BY id;

-- Case Fact Table
CREATE TABLE IF NOT EXISTS crime_analytics.fact_case (
    id UInt64,
    case_number String,
    date_id String,
    time_id String,
    crime_id Nullable(UInt64),
    location_id Nullable(UInt64),
    patrol_unit_id Nullable(UInt64),
    arrest UInt8,
    domestic UInt8
) ENGINE = MergeTree()
ORDER BY (date_id, time_id, id)
PARTITION BY substring(date_id, 1, 6);
