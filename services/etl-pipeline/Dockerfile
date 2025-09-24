# Dockerfile for ETL Pipeline Service

# Use a base image with Spark and Python
FROM bitnami/spark:3-python

# Set the working directory
WORKDIR /app

# Copy the job scripts and requirements
COPY ./jobs /app/jobs
COPY ./jobs/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# The entrypoint would typically be a script that runs spark-submit
# For example:
# ENTRYPOINT ["spark-submit", "/app/jobs/main_etl_job.py"]

# For now, a placeholder command
CMD ["bash", "-c", "echo 'ETL Service Ready. Submit jobs via spark-submit.' && tail -f /dev/null"]
