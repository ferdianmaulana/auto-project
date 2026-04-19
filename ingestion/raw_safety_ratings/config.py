GCP_PROJECT = "auto-project"
BQ_DATASET = "raw"
BQ_TABLE = "safety_ratings"

BASE_URL = "https://api.nhtsa.gov"

# Safety ratings uses path params — template instead of single endpoint
API_ENDPOINT_TEMPLATE = "/SafetyRatings/modelyear/{year}/make/{make}/model/{model}"

VEHICLE_SCOPE = {
    "Toyota":     ["Camry", "Corolla", "RAV4", "Highlander", "Tacoma"],
    "Honda":      ["Civic", "Accord", "CR-V", "Pilot", "Odyssey"],
    "Ford":       ["F-150", "Mustang", "Explorer", "Escape", "Edge"],
    "Chevrolet":  ["Silverado", "Malibu", "Equinox", "Traverse", "Tahoe"],
    "BMW":        ["3 Series", "5 Series", "X3", "X5", "X1"],
    "Mercedes":   ["C-Class", "E-Class", "GLC", "GLE", "A-Class"],
    "Volkswagen": ["Jetta", "Passat", "Tiguan", "Atlas", "Golf"],
}

MODEL_YEARS = list(range(2015, 2025))

UNIQUE_ID_FIELD = "VehicleId"

WRITE_MODE = "APPEND"

VALIDATION_CHECKS = {
    "no_null_vehicleId":       "SELECT COUNT(*) FROM `{table_id}` WHERE VehicleId IS NULL",
    "no_null_make":            "SELECT COUNT(*) FROM `{table_id}` WHERE make IS NULL",
    "no_null_model":           "SELECT COUNT(*) FROM `{table_id}` WHERE model IS NULL",
    "no_null_modelYear":       "SELECT COUNT(*) FROM `{table_id}` WHERE modelYear IS NULL",
    "valid_model_year_range":  "SELECT COUNT(*) FROM `{table_id}` WHERE modelYear < 2015 OR modelYear > 2024",
    "minimum_row_count":       "SELECT IF(COUNT(*) < 10, 1, 0) FROM `{table_id}`",
}