GCP_PROJECT = "auto-project"
BQ_DATASET  = "raw"
BQ_TABLE    = "vehicles"

API_ENDPOINT = "/vehicles"

# Master data — use TRUNCATE to always have fresh master
WRITE_MODE = "TRUNCATE"

VALIDATION_CHECKS = {
    "no_null_vehicle_id":   "SELECT COUNT(*) FROM `{table_id}` WHERE vehicle_id IS NULL",
    "no_null_brand":        "SELECT COUNT(*) FROM `{table_id}` WHERE brand IS NULL",
    "no_null_model":        "SELECT COUNT(*) FROM `{table_id}` WHERE model IS NULL",
    "no_null_plate":        "SELECT COUNT(*) FROM `{table_id}` WHERE plate_number IS NULL",
    "no_null_year":         "SELECT COUNT(*) FROM `{table_id}` WHERE year IS NULL",
    "valid_year_range":     "SELECT COUNT(*) FROM `{table_id}` WHERE year < 2018 OR year > 2024",
    "minimum_row_count":    "SELECT IF(COUNT(*) < 100, 1, 0) FROM `{table_id}`",
}