from google.cloud.bigquery import SchemaField

SCHEMA = [
    SchemaField(
        "item_id",
        "STRING",
        mode="REQUIRED",
        description="Unique item identifier — format: ITM-{YYYYMMDD}-{ORDER_SEQ}-{ITEM_SEQ}",
    ),
    SchemaField(
        "order_id",
        "STRING",
        mode="REQUIRED",
        description="Parent service order ID — FK to raw_service_orders.order_id",
    ),
    SchemaField(
        "order_date",
        "DATE",
        mode="REQUIRED",
        description="Date of the parent service order — denormalized for partitioning",
    ),
    SchemaField(
        "item_type",
        "STRING",
        mode="REQUIRED",
        description="Type of line item — Part, Labor, Fluid, or Consumable",
    ),
    SchemaField(
        "part_number",
        "STRING",
        mode="NULLABLE",
        description="Part number — FK to raw_spare_parts.part_number, LBR-001 for labor",
    ),
    SchemaField(
        "part_name",
        "STRING",
        mode="REQUIRED",
        description="Human readable part or labor description",
    ),
    SchemaField(
        "category",
        "STRING",
        mode="NULLABLE",
        description="Part category or Labor for labor line items",
    ),
    SchemaField(
        "quantity",
        "INTEGER",
        mode="NULLABLE",
        description="Quantity of parts used or 1 for labor",
    ),
    SchemaField(
        "unit_price",
        "FLOAT",
        mode="NULLABLE",
        description="Unit price in IDR per part or total labor rate",
    ),
    SchemaField(
        "total_price",
        "FLOAT",
        mode="NULLABLE",
        description="Total line item price in IDR — unit_price × quantity",
    ),
    SchemaField(
        "is_warranty",
        "BOOLEAN",
        mode="NULLABLE",
        description="Whether this line item is covered under warranty",
    ),
    SchemaField(
        "ingested_at",
        "TIMESTAMP",
        mode="NULLABLE",
        description="UTC timestamp when this record was ingested into BigQuery",
    ),
]