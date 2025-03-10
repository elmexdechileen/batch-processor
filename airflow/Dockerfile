FROM apache/airflow:2.10.5

# Install any additional dependencies if needed
# RUN pip install <your-dependencies>

# Set the working directory
WORKDIR /opt/airflow

USER root

# Install build tools and gcc
RUN apt-get update && apt-get install -y build-essential gcc

USER airflow

RUN /usr/local/bin/python -m pip install --upgrade pip
# Install dbt-core
RUN pip install --upgrade pip && pip install --no-cache-dir dbt-core dbt-postgres
# Copy your Airflow configuration files if needed
# COPY airflow.cfg /opt/airflow/airflow.cfg

# Expose the port Airflow web server runs on
EXPOSE 8080

# Empty entrypoint to avoid the gunicorn start command
ENTRYPOINT []
