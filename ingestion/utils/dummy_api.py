import os

def get_dummy_api_url() -> str:
    """
    Returns the Dummy API base URL from environment variable.
    Falls back to localhost for local testing.
    """
    return os.getenv("AUTO_API_URL", "http://localhost:8000")