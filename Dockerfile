FROM apache/airflow:2.8.1

USER root

# Install git — required by dbt deps
RUN apt-get update && apt-get install -y git && apt-get clean

# Copy requirements to airflow working directory
COPY requirements.txt /opt/airflow/requirements.txt

# Install packages as airflow user
USER airflow

RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt