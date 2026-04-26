GCP_PROJECT = "auto-project"
BQ_DATASET  = "raw"
BQ_TABLE    = "sales_orders"

API_ENDPOINT = "/sales-orders"

WRITE_MODE = "APPEND"

VALIDATION_CHECKS = {
    "no_null_sale_id":          "SELECT COUNT(*) FROM `{table_id}` WHERE sale_id IS NULL",
    "no_null_sale_date":        "SELECT COUNT(*) FROM `{table_id}` WHERE sale_date IS NULL",
    "no_null_dealer_id":        "SELECT COUNT(*) FROM `{table_id}` WHERE dealer_id IS NULL",
    "no_null_vehicle_id":       "SELECT COUNT(*) FROM `{table_id}` WHERE vehicle_id IS NULL",
    "no_negative_final_price":  "SELECT COUNT(*) FROM `{table_id}` WHERE final_price < 0",
    "no_negative_discount":     "SELECT COUNT(*) FROM `{table_id}` WHERE discount < 0",
    "valid_sale_type":          """
        SELECT COUNT(*) FROM `{table_id}`
        WHERE sale_type NOT IN ('Cash', 'Credit', 'Leasing')
    """,
    "minimum_row_count":        "SELECT IF(COUNT(*) < 5, 1, 0) FROM `{table_id}`",
}