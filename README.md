# Crime & Public Security Analysis

This project is a comprehensive data platform for analyzing crime and public security data. It includes data ingestion, ETL processing, machine learning modeling, and a web-based dashboard for visualization and decision support.

## Project Structure

The project is organized into a microservices architecture to promote separation of concerns and independent development.

-   `/data`: Contains raw and processed datasets.
-   `/docs`: Project documentation, including architecture and API specs.
-   `/infra`: Infrastructure-as-Code configurations for services like Cassandra, Kafka, etc.
-   `/services`: Core application logic, with each service in its own directory.
-   `/services-ingestion`: A dedicated service for initial data ingestion.

## Getting Started

### Prerequisites

-   Docker
-   Docker Compose

### Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Configure environment variables:**
    Copy the example environment file and update it with your local configuration.
    ```bash
    cp .env.example .env
    ```

3.  **Build and run the services:**
    ```bash
    docker-compose up --build
    ```

This will start all the services defined in the `docker-compose.yml` file.

## Services

-   **Data Ingestion API (`services-ingestion`):** FastAPI service to upload and initially process raw CSV data.
-   **ETL Pipeline (`services/etl-pipeline`):** Spark jobs for transforming and moving data from Cassandra to the Clickhouse data warehouse.
-   **ML Service (`services/ml-service`):** Handles training and serving of machine learning models.
-   **Web API (`services/web-api`):** FastAPI backend that serves data to the frontend dashboard.
-   **Web Frontend (`services/web-frontend`):** ReactJS application for data visualization and user interaction.

For more details on a specific service, please refer to the `README.md` within its directory.
