GCP_PROJECT = "auto-project-493707"
BQ_DATASET  = "raw"
BQ_TABLE    = "service_orders"

API_ENDPOINT = "/service-orders"

# Daily transactions — use APPEND for full history
WRITE_MODE = "APPEND"

VALIDATION_CHECKS = {
    "no_null_order_id":         "SELECT COUNT(*) FROM `{table_id}` WHERE order_id IS NULL",
    "no_null_order_date":       "SELECT COUNT(*) FROM `{table_id}` WHERE order_date IS NULL",
    "no_null_dealer_id":        "SELECT COUNT(*) FROM `{table_id}` WHERE dealer_id IS NULL",
    "no_null_vehicle_id":       "SELECT COUNT(*) FROM `{table_id}` WHERE vehicle_id IS NULL",
    "no_null_service_type":     "SELECT COUNT(*) FROM `{table_id}` WHERE service_type IS NULL",
    "no_negative_total_cost":   "SELECT COUNT(*) FROM `{table_id}` WHERE total_cost < 0",
    "valid_status":             """
        SELECT COUNT(*) FROM `{table_id}`
        WHERE status NOT IN ('Open', 'In Progress', 'Completed', 'Cancelled')
    """,
    "valid_service_type":       """
        SELECT COUNT(*) FROM `{table_id}`
        WHERE service_type NOT IN ('Periodic', 'Repair', 'Body & Paint', 'PDI', 'Recall')
    """,
    "minimum_row_count":        "SELECT IF(COUNT(*) < 10, 1, 0) FROM `{table_id}`",
}