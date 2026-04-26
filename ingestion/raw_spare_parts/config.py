GCP_PROJECT = "auto-project"
BQ_DATASET  = "raw"
BQ_TABLE    = "spare_parts"

API_ENDPOINT = "/spare-parts"

WRITE_MODE = "TRUNCATE"

VALIDATION_CHECKS = {
    "no_null_part_number":  "SELECT COUNT(*) FROM `{table_id}` WHERE part_number IS NULL",
    "no_null_part_name":    "SELECT COUNT(*) FROM `{table_id}` WHERE part_name IS NULL",
    "no_null_category":     "SELECT COUNT(*) FROM `{table_id}` WHERE category IS NULL",
    "no_negative_price":    "SELECT COUNT(*) FROM `{table_id}` WHERE unit_price < 0",
    "minimum_row_count":    "SELECT IF(COUNT(*) < 10, 1, 0) FROM `{table_id}`",
}