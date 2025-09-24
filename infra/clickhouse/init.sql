-- Create the main database if it doesn't exist
CREATE DATABASE IF NOT EXISTS crime_data;

-- Use the database
USE crime_data;

-- Create a table for aggregated crime statistics by area
CREATE TABLE IF NOT EXISTS crime_stats_by_area (
    area_id String,
    report_month Date,
    crime_type String,
    incident_count UInt64,
    poverty_rate Float32,
    unemployment_rate Float32,
    population UInt64
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(report_month)
ORDER BY (area_id, report_month, crime_type);

-- Create a table for crime hotspot predictions
CREATE TABLE IF NOT EXISTS crime_hotspots (
    hotspot_id String,
    prediction_date Date,
    latitude Float64,
    longitude Float64,
    predicted_crime_level UInt8,
    confidence_score Float32
) ENGINE = MergeTree()
ORDER BY (prediction_date, hotspot_id);
