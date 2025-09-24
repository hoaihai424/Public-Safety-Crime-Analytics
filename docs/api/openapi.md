# OpenAPI Specification

This document provides the OpenAPI (formerly Swagger) specification for the various APIs within this project.

## Web API

(Link to or include the OpenAPI 3.0 specification for the `web-api` service here. This should detail all the endpoints served to the frontend.)

```yaml
openapi: 3.0.0
info:
  title: Crime Analysis Web API
  version: 1.0.0
paths:
  /api/crimes:
    get:
      summary: Retrieve a list of crimes
      responses:
        '200':
          description: A list of crimes.
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
# ... more definitions
```

## Data Ingestion API

(Link to or include the OpenAPI 3.0 specification for the `services-ingestion` API.)

```yaml
openapi: 3.0.0
info:
  title: Data Ingestion API
  version: 1.0.0
paths:
  /upload/csv:
    post:
      summary: Upload a CSV file for processing
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
      responses:
        '202':
          description: File accepted for processing.
# ... more definitions
```
