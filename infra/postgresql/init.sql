-- init database for postgresql
CREATE DATABASE crime_data;
\c crime_data;

-- Create primary type table
CREATE TABLE IF NOT EXISTS primary_type (
    id UUID PRIMARY KEY,
    name TEXT
);  

-- Create crime table
CREATE TABLE IF NOT EXISTS crime (
    id UUID PRIMARY KEY,
    iucr TEXT,
    fbi_code TEXT,
    primary_type UUID REFERENCES primary_type(id),
    description TEXT
);  

CREATE INDEX IF NOT EXISTS crimes_iucr_idx ON crime (iucr);
CREATE INDEX IF NOT EXISTS crimes_primary_type_idx ON crime (primary_type);

-- Create location table
CREATE TABLE IF NOT EXISTS location (
    id UUID PRIMARY KEY,
    location TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    block TEXT,
    location_description TEXT
);

CREATE INDEX IF NOT EXISTS location_description_idx ON location (location_description);
CREATE INDEX IF NOT EXISTS locations_block_idx ON location (block);

-- Create patrol unit table
CREATE TABLE IF NOT EXISTS patrol_unit (
    id UUID PRIMARY KEY,
    beat TEXT,
    district TEXT,
    ward TEXT,
    community_area TEXT
);

CREATE INDEX IF NOT EXISTS patrol_units_beat_idx ON patrol_unit (beat);
CREATE INDEX IF NOT EXISTS patrol_units_district_idx ON patrol_unit (district);

-- Create case table
CREATE TABLE IF NOT EXISTS case_report (
    id UUID PRIMARY KEY,
    case_number TEXT,
    arrest_made BOOLEAN,
    domestic BOOLEAN,
    incident_time TIMESTAMP,
    location UUID REFERENCES location(id),
    patrol_unit UUID REFERENCES patrol_unit(id),
    crime UUID REFERENCES crime(id)
);

CREATE INDEX IF NOT EXISTS cases_case_number_idx ON case_report (case_number);
CREATE INDEX IF NOT EXISTS cases_crime_idx ON case_report (crime);
CREATE INDEX IF NOT EXISTS cases_location_idx ON case_report (location);
CREATE INDEX IF NOT EXISTS cases_patrol_unit_idx ON case_report (patrol_unit);


