# Data Ingestion Service

This service is responsible for the initial ingestion of raw data into the system.

## Technology

-   FastAPI for serving the API.
-   Pandas for initial CSV processing.

## Responsibilities

-   Provide an API endpoint to upload CSV files.
-   Perform basic validation and cleaning of the raw data.
-   Insert the cleaned data into the Cassandra database.

## Directories

-   `/src`: The FastAPI application code.
-   `/tests`: Tests for the service.

## API Endpoints

-   `POST /upload/csv`: Accepts a multipart/form-data request with a CSV file.
