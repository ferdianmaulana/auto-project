GCP_PROJECT = "auto-project-493707"
BQ_DATASET  = "raw"
BQ_TABLE    = "warranty_claims"

API_ENDPOINT = "/warranty-claims"

WRITE_MODE = "APPEND"

VALIDATION_CHECKS = {
    "no_null_claim_id":     "SELECT COUNT(*) FROM `{table_id}` WHERE claim_id IS NULL",
    "no_null_claim_date":   "SELECT COUNT(*) FROM `{table_id}` WHERE claim_date IS NULL",
    "no_null_vehicle_id":   "SELECT COUNT(*) FROM `{table_id}` WHERE vehicle_id IS NULL",
    "no_null_component":    "SELECT COUNT(*) FROM `{table_id}` WHERE component IS NULL",
    "no_negative_amount":   "SELECT COUNT(*) FROM `{table_id}` WHERE claim_amount < 0",
    "valid_claim_status":   """
        SELECT COUNT(*) FROM `{table_id}`
        WHERE claim_status NOT IN ('Submitted', 'Approved', 'Rejected', 'Paid')
    """,
    "valid_claim_type":     """
        SELECT COUNT(*) FROM `{table_id}`
        WHERE claim_type NOT IN ('Parts', 'Labor', 'Both')
    """,
    "minimum_row_count":    "SELECT IF(COUNT(*) < 3, 1, 0) FROM `{table_id}`",
}