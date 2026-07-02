"""Configuration loading for the tools server.

Configuration is represented as a plain immutable dict and loaded from
environment variables. Keeping it a plain value (rather than a class) makes it
trivial to pass explicitly into the functions that need it.
"""
from __future__ import annotations

import os
from types import MappingProxyType
from typing import Mapping

# Default RapidAPI host for the "Streaming Availability" API.
_DEFAULT_HOST = "streaming-availability.p.rapidapi.com"


def load_config() -> Mapping[str, object]:
    """Build the read-only application configuration from the environment.

    Reads the following environment variables:
      - RAPIDAPI_KEY       (required at request time) the RapidAPI key.
      - RAPIDAPI_HOST      (optional) the RapidAPI host to call.
      - REQUEST_TIMEOUT    (optional) upstream request timeout in seconds.
      - DEFAULT_COUNTRY    (optional) fallback two-letter country code.

    Returns:
        Mapping[str, object]: A read-only mapping of configuration values.
    """
    config = {
        "rapidapi_key": os.environ.get("RAPIDAPI_KEY", ""),
        "rapidapi_host": os.environ.get("RAPIDAPI_HOST", _DEFAULT_HOST),
        "request_timeout": int(os.environ.get("REQUEST_TIMEOUT", "10")),
        "default_country": os.environ.get("DEFAULT_COUNTRY", "us").lower(),
    }
    return MappingProxyType(config)
