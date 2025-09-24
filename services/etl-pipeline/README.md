# ETL Pipeline Service

This service is responsible for running the Extract, Transform, Load (ETL) jobs that process data from the primary data store (Cassandra) and load it into the analytical data warehouse (Clickhouse).

## Technology

-   Apache Spark for distributed data processing.
-   Python with Pandas for data manipulation.

## Jobs

-   `/jobs`: This directory contains the individual Spark job scripts.
    -   `placeholder.md`: A placeholder for your first ETL job, e.g., `cassandra_to_clickhouse.py`.

## How to Run

ETL jobs are typically triggered on a schedule or in response to an event. For local development, you can run them manually using `docker-compose exec`.

1.  **Access the Spark container:**
    ```bash
    docker-compose exec <spark_container_name> bash
    ```

2.  **Submit a job:**
    Inside the container, use `spark-submit` to run a job.
    ```bash
    spark-submit \
      --master local[*]
      /app/jobs/your_etl_job.py
    ```

