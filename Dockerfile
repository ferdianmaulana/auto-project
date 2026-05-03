FROM apache/airflow:2.8.1

USER root

# Install git — required by dbt deps
RUN apt-get update && apt-get install -y git && apt-get clean

USER airflow

WORKDIR /home/airflow

COPY requirements.txt /home/airflow/requirements.txt
RUN pip install --no-cache-dir -r /home/airflow/requirements.txt