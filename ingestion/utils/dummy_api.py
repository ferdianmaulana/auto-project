import os
import time
import requests
from utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_TIMEOUT = 30
DEFAULT_DELAY   = 0.5


def get_dummy_api_url() -> str:
    """
    Returns the Dummy API base URL from environment variable.
    Falls back to localhost for local testing.
    """
    return os.getenv("AUTO_API_URL", "http://localhost:8000")


def call_api_with_retry(
    base_url: str,
    endpoint: str,
    params: dict = None,
    headers: dict = None,
    timeout: int = DEFAULT_TIMEOUT,
    delay: float = DEFAULT_DELAY,
    max_retries: int = 3,
    retry_delay: float = 5.0,
) -> dict:
    """
    Generic REST API GET caller with retry logic.
    """
    url = f"{base_url}{endpoint}"

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers or {},
                timeout=timeout,
            )
            response.raise_for_status()
            time.sleep(delay)
            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling {url}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code} calling {url}: {e}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error calling {url}")
        except Exception as e:
            logger.error(f"Unexpected error calling {url}: {e}")

        if attempt < max_retries:
            logger.warning(
                f"Attempt {attempt}/{max_retries} failed — "
                f"retrying in {retry_delay}s..."
            )
            time.sleep(retry_delay)

    logger.error(f"All {max_retries} attempts failed for {url}")
    return {}