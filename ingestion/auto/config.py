VEHICLE_SCOPE = {
    "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Tacoma"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Odyssey"],
    "Ford": ["F-150", "Mustang", "Explorer", "Escape", "Edge"],
    "Chevrolet": ["Silverado", "Malibu", "Equinox", "Traverse", "Tahoe"],
    "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Palisade"],
    "Nissan": ["Altima", "Sentra", "Rogue", "Pathfinder", "Frontier"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "X1"],
    "Mercedes": ["C-Class", "E-Class", "GLC", "GLE", "A-Class"],
    "Kia": ["Optima", "Sorento", "Sportage", "Telluride", "Soul"],
    "Volkswagen": ["Jetta", "Passat", "Tiguan", "Atlas", "Golf"],
}

import datetime
MODEL_YEARS = list(range(2015, datetime.date.today().year))

BASE_URL = "https://api.nhtsa.gov"

BIGQUERY_PROJECT = "auto-project"  # replace with your GCP project ID
BIGQUERY_DATASET_RAW = "raw"

# Request settings
REQUEST_TIMEOUT = 30        # seconds
REQUEST_DELAY = 0.5         # seconds between API calls to avoid rate limiting