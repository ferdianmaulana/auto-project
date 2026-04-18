FROM apache/airflow:2.8.1

USER airflow

RUN pip install --no-cache-dir \
    requests \
    pandas \
    dbt-core==1.7.4 \
    dbt-duckdb==1.7.2 \
    duckdb==0.10.0 \
    great-expectations==0.18.8
