from google.cloud.bigquery import SchemaField

SCHEMA = [
    SchemaField(
        "vehicle_id",
        "STRING",
        mode="REQUIRED",
        description="Unique vehicle identifier — format: VH-{BRAND}-{MODEL}-{YEAR}-{SEQ}",
    ),
    SchemaField(
        "vin",
        "STRING",
        mode="NULLABLE",
        description="Vehicle Identification Number — 17 character unique code",
    ),
    SchemaField(
        "plate_number",
        "STRING",
        mode="NULLABLE",
        description="Indonesian vehicle plate number — format: {PREFIX} {NNNN} {AAA}",
    ),
    SchemaField(
        "brand",
        "STRING",
        mode="REQUIRED",
        description="Vehicle manufacturer brand — e.g. Toyota, Honda, BMW",
    ),
    SchemaField(
        "model",
        "STRING",
        mode="REQUIRED",
        description="Vehicle model name — e.g. Avanza, Civic, X3",
    ),
    SchemaField(
        "variant",
        "STRING",
        mode="NULLABLE",
        description="Vehicle variant/trim level — e.g. 1.5 G CVT, M Sport",
    ),
    SchemaField(
        "year",
        "INTEGER",
        mode="REQUIRED",
        description="Vehicle manufacturing year — range 2018–2024",
    ),
    SchemaField(
        "color",
        "STRING",
        mode="NULLABLE",
        description="Exterior color of the vehicle",
    ),
    SchemaField(
        "engine_cc",
        "INTEGER",
        mode="NULLABLE",
        description="Engine displacement in cubic centimeters — 0 for electric vehicles",
    ),
    SchemaField(
        "fuel_type",
        "STRING",
        mode="NULLABLE",
        description="Fuel type — Gasoline, Diesel, Electric, or Hybrid",
    ),
    SchemaField(
        "transmission",
        "STRING",
        mode="NULLABLE",
        description="Transmission type — Manual, Automatic, or CVT",
    ),
    SchemaField(
        "purchase_date",
        "DATE",
        mode="NULLABLE",
        description="Date vehicle was first purchased by owner",
    ),
    SchemaField(
        "owner_city",
        "STRING",
        mode="NULLABLE",
        description="City where the vehicle owner is located",
    ),
    SchemaField(
        "dealer_id",
        "STRING",
        mode="NULLABLE",
        description="Dealer ID where vehicle was purchased — FK to dealers master",
    ),
    SchemaField(
        "ingested_at",
        "TIMESTAMP",
        mode="NULLABLE",
        description="UTC timestamp when this record was ingested into BigQuery",
    ),
]