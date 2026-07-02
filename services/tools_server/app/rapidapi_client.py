"""Client functions for the RapidAPI "Streaming Availability" API.

This module isolates all knowledge of the external API: how to authenticate,
which path to call, and how to reshape the raw upstream payload into the small,
stable structure our own endpoints return. Everything here is a pure-ish
function that takes configuration explicitly, so it is easy to test and reuse.
"""
from __future__ import annotations

from typing import Any, List, Mapping

import requests


class UpstreamError(Exception):
    """Raised when the upstream RapidAPI request fails.

    Attributes:
        status_code: The HTTP status to surface to the caller (defaults to 502).
    """

    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


def _auth_headers(config: Mapping[str, object]) -> Mapping[str, str]:
    """Build the RapidAPI authentication headers from configuration.

    Args:
        config: The application configuration mapping.

    Returns:
        Mapping[str, str]: Headers containing the RapidAPI key and host.
    """
    return {
        "X-RapidAPI-Key": str(config["rapidapi_key"]),
        "X-RapidAPI-Host": str(config["rapidapi_host"]),
    }


def _extract_options(show: Mapping[str, Any], country: str) -> List[dict]:
    """Reduce a raw upstream "show" object into a flat list of stream options.

    Args:
        show: A single show object from the RapidAPI response.
        country: The two-letter country code whose options to extract.

    Returns:
        List[dict]: One entry per streaming option with service, type,
        price and link keys.
    """
    raw_options = show.get("streamingOptions", {}).get(country, [])
    return [
        {
            "service": opt.get("service", {}).get("name"),
            "type": opt.get("type"),
            "price": opt.get("price", {}).get("formatted"),
            "link": opt.get("link"),
        }
        for opt in raw_options
    ]


def fetch_streaming_availability(
    config: Mapping[str, object], title: str, country: str
) -> dict:
    """Look up live streaming availability for a title via RapidAPI.

    Args:
        config: The application configuration mapping.
        title: The show or movie title to search for.
        country: The two-letter country code to search within.

    Returns:
        dict: A payload of the form
        ``{"title": str, "country": str, "streamingOptions": list}``.
        The streamingOptions list is empty when the title has no options.

    Raises:
        UpstreamError: If the upstream request fails or returns no matches.
    """
    host = config["rapidapi_host"]
    try:
        resp = requests.get(
            f"https://{host}/shows/search/title",
            headers=_auth_headers(config),
            params={
                "title": title,
                "country": country,
                "series_granularity": "show",
                "output_language": "en",
            },
            timeout=config["request_timeout"],
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise UpstreamError(f"upstream API error: {exc}") from exc

    data = resp.json()
    if not data:
        raise UpstreamError(f"no results for '{title}'", status_code=404)

    show = data[0]
    return {
        "title": show.get("title"),
        "country": country,
        "streamingOptions": _extract_options(show, country),
    }
