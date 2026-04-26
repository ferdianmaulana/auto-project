from google.cloud.bigquery import SchemaField

SCHEMA = [
    SchemaField(
        "claim_id",
        "STRING",
        mode="REQUIRED",
        description="Unique warranty claim identifier — format: WC-{YYYYMMDD}-{SEQ}",
    ),
    SchemaField(
        "claim_date",
        "DATE",
        mode="REQUIRED",
        description="Date the warranty claim was submitted",
    ),
    SchemaField(
        "vehicle_id",
        "STRING",
        mode="REQUIRED",
        description="Vehicle identifier — FK to raw_vehicles.vehicle_id",
    ),
    SchemaField(
        "brand",
        "STRING",
        mode="NULLABLE",
        description="Vehicle brand — denormalized from vehicles for query convenience",
    ),
    SchemaField(
        "model",
        "STRING",
        mode="NULLABLE",
        description="Vehicle model — denormalized from vehicles for query convenience",
    ),
    SchemaField(
        "model_year",
        "INTEGER",
        mode="NULLABLE",
        description="Vehicle manufacturing year — denormalized from vehicles",
    ),
    SchemaField(
        "purchase_date",
        "DATE",
        mode="NULLABLE",
        description="Original vehicle purchase date — used to verify warranty eligibility",
    ),
    SchemaField(
        "dealer_id",
        "STRING",
        mode="NULLABLE",
        description="Dealer ID where claim was submitted — FK to dealers master",
    ),
    SchemaField(
        "claim_type",
        "STRING",
        mode="NULLABLE",
        description="What the claim covers — Parts, Labor, or Both",
    ),
    SchemaField(
        "component",
        "STRING",
        mode="NULLABLE",
        description="Vehicle component with defect — Engine, Brakes, AC System, etc.",
    ),
    SchemaField(
        "defect_description",
        "STRING",
        mode="NULLABLE",
        description="Customer reported description of the defect or issue",
    ),
    SchemaField(
        "claim_status",
        "STRING",
        mode="NULLABLE",
        description="Current claim status — Submitted, Approved, Rejected, or Paid",
    ),
    SchemaField(
        "claim_amount",
        "FLOAT",
        mode="NULLABLE",
        description="Total claim amount requested in IDR",
    ),
    SchemaField(
        "approved_amount",
        "FLOAT",
        mode="NULLABLE",
        description="Amount approved for reimbursement in IDR — 0 if Rejected",
    ),
    SchemaField(
        "ingested_at",
        "TIMESTAMP",
        mode="NULLABLE",
        description="UTC timestamp when this record was ingested into BigQuery",
    ),
]