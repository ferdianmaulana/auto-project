GCP_PROJECT = "auto-project-493707"
BQ_DATASET  = "raw"
BQ_TABLE    = "service_order_items"

API_ENDPOINT = "/service-order-items"

WRITE_MODE = "APPEND"

VALIDATION_CHECKS = {
    "no_null_item_id":      "SELECT COUNT(*) FROM `{table_id}` WHERE item_id IS NULL",
    "no_null_order_id":     "SELECT COUNT(*) FROM `{table_id}` WHERE order_id IS NULL",
    "no_null_item_type":    "SELECT COUNT(*) FROM `{table_id}` WHERE item_type IS NULL",
    "no_null_part_name":    "SELECT COUNT(*) FROM `{table_id}` WHERE part_name IS NULL",
    "no_negative_price":    "SELECT COUNT(*) FROM `{table_id}` WHERE total_price < 0",
    "valid_item_type":      """
        SELECT COUNT(*) FROM `{table_id}`
        WHERE item_type NOT IN ('Part', 'Labor', 'Fluid', 'Consumable')
    """,
    "minimum_row_count":    "SELECT IF(COUNT(*) < 10, 1, 0) FROM `{table_id}`",
}