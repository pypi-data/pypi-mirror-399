from typing import Any, Dict

import requests

from ..utils.messages import print_verbose


def get(url: str, verbose: bool = False, **kwargs: Any) -> Dict[str, Any]:
    """
    Get JSON data from a URL using HTTP GET request.

    Args:
        url: The URL to fetch JSON data from (must be non-empty string).
        verbose: If True, prints error messages.
        **kwargs: Additional keyword arguments passed to requests.get().

    Returns:
        Dictionary containing the JSON response.

    Raises:
        ValueError: If url is empty or not a string.
        requests.RequestException: If the HTTP request fails.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty string")

    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()  # Raise exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print_verbose(f"Error fetching JSON from {url}: {e}", verbose=verbose)
        raise
