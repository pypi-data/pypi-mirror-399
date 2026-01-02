"""HTTP transport for sending error events."""

import json
import logging
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

logger = logging.getLogger("proliferate")


def send_event(endpoint: str, payload: dict[str, Any]) -> bool:
    """
    Send event payload to the API endpoint.

    Synchronous HTTP POST. Fire and forget - does not retry on failure.

    Args:
        endpoint: API endpoint URL
        payload: Event payload dictionary

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        data = json.dumps(payload).encode("utf-8")
        request = Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urlopen(request, timeout=5) as response:
            return bool(response.status == 202)

    except URLError as e:
        logger.debug(f"Failed to send event: {e}")
        return False
    except Exception as e:
        logger.debug(f"Unexpected error sending event: {e}")
        return False
