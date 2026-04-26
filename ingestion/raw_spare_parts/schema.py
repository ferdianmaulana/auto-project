from google.cloud.bigquery import SchemaField

SCHEMA = [
    SchemaField(
        "part_number",
        "STRING",
        mode="REQUIRED",
        description="Unique part identifier — format: PRT-{CATEGORY}-{SEQ}",
    ),
    SchemaField(
        "part_name",
        "STRING",
        mode="REQUIRED",
        description="Human readable part name — e.g. Engine Oil Filter, Brake Pad Front",
    ),
    SchemaField(
        "category",
        "STRING",
        mode="REQUIRED",
        description="Part category — Engine, Brakes, Suspension, AC System, Electrical, Transmission, Cooling, Tires",
    ),
    SchemaField(
        "unit_price",
        "FLOAT",
        mode="REQUIRED",
        description="Genuine part price in IDR (Indonesian Rupiah)",
    ),
    SchemaField(
        "unit",
        "STRING",
        mode="NULLABLE",
        description="Unit of measurement — pcs, liter, set, meter, can",
    ),
    SchemaField(
        "ingested_at",
        "TIMESTAMP",
        mode="NULLABLE",
        description="UTC timestamp when this record was ingested into BigQuery",
    ),
]