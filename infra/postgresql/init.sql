-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS case_report CASCADE;
DROP TABLE IF EXISTS patrol_unit CASCADE;
DROP TABLE IF EXISTS location CASCADE;
DROP TABLE IF EXISTS crime CASCADE;
DROP TABLE IF EXISTS primary_type CASCADE;

-- Create primary_type table
CREATE TABLE primary_type (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE INDEX idx_primary_type_name ON primary_type(name);

-- Create crime table
CREATE TABLE crime (
    id BIGINT PRIMARY KEY,
    iucr TEXT,
    primary_type BIGINT REFERENCES primary_type(id),
    description TEXT,
    fbi_code TEXT
);

CREATE INDEX idx_crime_iucr ON crime(iucr);
CREATE INDEX idx_crime_primary_type ON crime(primary_type);
CREATE INDEX idx_crime_fbi_code ON crime(fbi_code);

-- Create location table
CREATE TABLE location (
    id BIGINT PRIMARY KEY,
    location_description TEXT,
    block TEXT,
    location TEXT
);

CREATE INDEX idx_location_description ON location(location_description);
CREATE INDEX idx_location_block ON location(block);
CREATE INDEX idx_location_coordinates ON location(latitude, longitude);

-- Create patrol_unit table
CREATE TABLE patrol_unit (
    id BIGINT PRIMARY KEY,
    beat INTEGER DEFAULT -1,
    district INTEGER DEFAULT -1,
    ward INTEGER DEFAULT -1,
    community_area INTEGER DEFAULT -1
);

CREATE INDEX idx_patrol_unit_beat ON patrol_unit(beat);
CREATE INDEX idx_patrol_unit_district ON patrol_unit(district);
CREATE INDEX idx_patrol_unit_ward ON patrol_unit(ward);
CREATE INDEX idx_patrol_unit_community_area ON patrol_unit(community_area);

-- Create case_report table (renamed from 'case' to avoid SQL keyword conflict)
CREATE TABLE case_report (
    id BIGINT PRIMARY KEY,
    case_number TEXT NOT NULL,
    crime_id BIGINT REFERENCES crime(id),
    location_id BIGINT REFERENCES location(id),
    patrol_unit_id BIGINT REFERENCES patrol_unit(id),
    date DATE,
    time TEXT,
    arrest INTEGER DEFAULT 0,
    domestic INTEGER DEFAULT 0
);

CREATE INDEX idx_case_report_case_number ON case_report(case_number);
CREATE INDEX idx_case_report_crime_id ON case_report(crime_id);
CREATE INDEX idx_case_report_location_id ON case_report(location_id);
CREATE INDEX idx_case_report_patrol_unit_id ON case_report(patrol_unit_id);
CREATE INDEX idx_case_report_date ON case_report(date);
CREATE INDEX idx_case_report_arrest ON case_report(arrest);
CREATE INDEX idx_case_report_domestic ON case_report(domestic);

-- Create composite index for common queries
CREATE INDEX idx_case_report_date_crime ON case_report(date, crime_id);
CREATE INDEX idx_case_report_date_location ON case_report(date, location_id);
