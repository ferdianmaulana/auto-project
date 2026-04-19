import time
import requests
from utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_TIMEOUT = 30
DEFAULT_DELAY = 0.5


def call_api(
    base_url: str,
    endpoint: str,
    params: dict = None,
    headers: dict = None,
    timeout: int = DEFAULT_TIMEOUT,
    delay: float = DEFAULT_DELAY,
) -> dict:
    """
    Generic REST API GET caller.
    Can be used for any API — NHTSA, OpenMeteo, CoinGecko, etc.

    Args:
        base_url:  Base URL of the API e.g. "https://api.nhtsa.gov"
        endpoint:  Endpoint path e.g. "/complaints/complaintsByVehicle"
        params:    Query parameters as dict e.g. {"make": "toyota"}
        headers:   Request headers as dict e.g. {"Authorization": "Bearer token"}
        timeout:   Request timeout in seconds
        delay:     Delay between calls to avoid rate limiting

    Returns:
        Parsed JSON response as dict, or empty dict on failure
    """
    url = f"{base_url}{endpoint}"
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
        return {}
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code} calling {url}: {e}")
        return {}
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error calling {url}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error calling {url}: {e}")
        return {}


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
    Same as call_api but with automatic retry on failure.
    Useful for unstable APIs or rate-limited endpoints.

    Args:
        max_retries:  Number of retry attempts before giving up
        retry_delay:  Seconds to wait between retries
    """
    for attempt in range(1, max_retries + 1):
        result = call_api(base_url, endpoint, params, headers, timeout, delay)
        if result:
            return result
        if attempt < max_retries:
            logger.warning(
                f"Attempt {attempt}/{max_retries} failed — "
                f"retrying in {retry_delay}s..."
            )
            time.sleep(retry_delay)

    logger.error(f"All {max_retries} attempts failed for {endpoint}")
    return {}


def build_combinations(scope: dict, dimensions: list) -> list:
    """
    Builds a flat list of all combinations from a scope dict and extra dimensions.
    Generic — works for any nested scope structure.

    Example:
        scope = {"Toyota": ["Camry", "Corolla"], "Honda": ["Civic"]}
        dimensions = [2022, 2023]
        returns: [
            ("Toyota", "Camry", 2022), ("Toyota", "Camry", 2023),
            ("Toyota", "Corolla", 2022), ("Toyota", "Corolla", 2023),
            ("Honda", "Civic", 2022), ("Honda", "Civic", 2023),
        ]

    Args:
        scope:       Dict of {key: [values]} e.g. {make: [models]}
        dimensions:  List of extra values to combine e.g. [years]

    Returns:
        List of tuples with all combinations
    """
    combinations = []
    for key, values in scope.items():
        for value in values:
            for dim in dimensions:
                combinations.append((key, value, dim))
    return combinations