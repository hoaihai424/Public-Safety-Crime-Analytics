# Project Architecture

This document outlines the high-level architecture of the Crime & Public Security Analysis platform.

## System Overview

The system is designed as a distributed, microservices-based architecture. Data flows from an initial ingestion point through a processing pipeline and into a data warehouse, where it is then consumed by a machine learning service and a web frontend.

![System Diagram](placeholder_for_diagram.png)
*(A diagram showing the flow of data between services would be placed here)*

### Components

1.  **Data Ingestion (`services-ingestion`)**
    *   **Technology:** FastAPI
    *   **Responsibility:** Provides an API endpoint for uploading raw CSV data. Performs initial validation and cleaning before storing the data in the primary data store.

2.  **Primary Data Store**
    *   **Technology:** Apache Cassandra
    *   **Responsibility:** Stores the raw and lightly processed data. Chosen for its scalability and write performance.

3.  **ETL Pipeline (`services/etl-pipeline`)**
    *   **Technology:** Apache Spark, Kafka, Debezium
    *   **Responsibility:** Extracts data from Cassandra (potentially using CDC with Debezium/Kafka), performs complex transformations and aggregations, and loads the results into the data warehouse.

4.  **Data Warehouse**
    *   **Technology:** ClickHouse
    *   **Responsibility:** Stores the aggregated, analysis-ready data. Chosen for its high-performance analytical query capabilities.

5.  **Machine Learning Service (`services/ml-service`)**
    *   **Technology:** FastAPI, PyTorch/TensorFlow
    *   **Responsibility:** Provides an API for training ML models and serving predictions (classification, clustering, forecasting). It queries data from the ClickHouse warehouse.

6.  **Web API (`services/web-api`)**
    *   **Technology:** FastAPI
    *   **Responsibility:** Acts as a backend-for-frontend (BFF). It queries the data warehouse and the ML service to provide data in a format suitable for the user-facing dashboard.

7.  **Web Frontend (`services/web-frontend`)**
    *   **Technology:** ReactJS
    *   **Responsibility:** Provides the user interface for the Decision Support System, including dashboards, charts, and maps.

## Data Flow

1.  A user or automated process uploads a CSV file to the **Data Ingestion** service.
2.  The service processes the file and writes the data to **Cassandra**.
3.  Changes in Cassandra are captured by Debezium and published as events to a **Kafka** topic.
4.  The **ETL Pipeline** (Spark Streaming job) consumes from the Kafka topic.
5.  The Spark job transforms the data and loads it into **ClickHouse**.
6.  The **Web API** queries ClickHouse for dashboard data and the **ML Service** for predictions.
7.  The **Web Frontend** calls the Web API to get the data and renders the visualizations for the user.

## Containerization & Orchestration

*   **Technology:** Docker, Docker Compose
*   **Responsibility:** All services are containerized using Docker for consistency across development, testing, and production environments. Docker Compose is used to orchestrate the multi-container application for local development. The structure is designed to be easily migrated to Kubernetes for production deployment.
