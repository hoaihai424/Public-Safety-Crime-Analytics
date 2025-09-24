# Web API Service

This service acts as a Backend-for-Frontend (BFF). It provides the data required by the web-based dashboard.

## Technology

-   FastAPI for serving the API.

## Responsibilities

-   Query the ClickHouse data warehouse for aggregated crime statistics.
-   Call the ML Service to get predictions (e.g., crime hotspots).
-   Format the data in a way that is easy for the frontend to consume.

## Directories

-   `/src`: The FastAPI application code.
-   `/tests`: Tests for the service.

## API Endpoints

(Define the API endpoints here, e.g., using OpenAPI/Swagger documentation.)

-   `GET /api/dashboard/stats`
-   `GET /api/dashboard/hotspots`
-   `GET /api/crimes/by-area`
