"""
title: Netflix Live Streaming Lookup
description: Calls the local tools_server to answer live streaming questions (service, price, country) that the Netflix Shows knowledge base can't answer.

Note: Open WebUI requires the tool to be defined as a `Tools` class exposing a
nested `Valves` model. That class shape is dictated by the framework; the actual
logic below is kept as small, self-contained functions.
"""
import requests
from pydantic import BaseModel, Field


def _format_options(data: dict, country: str) -> str:
    """Render the tools_server payload into a human-readable summary.

    Args:
        data: The JSON payload returned by the tools_server /streaming route.
        country: The two-letter country code that was queried.

    Returns:
        str: A newline-separated summary of streaming options, or a message
        explaining that no options were found.
    """
    if not data.get("streamingOptions"):
        return f"No live streaming options found for '{data.get('title')}' in {country}."

    header = f"Live streaming options for '{data.get('title')}' ({country}):"
    lines = [
        f"- {o['service']}: {o['type']}" + (f" ({o['price']})" if o.get("price") else "")
        for o in data["streamingOptions"]
    ]
    return "\n".join([header, *lines])


class Tools:
    class Valves(BaseModel):
        server_url: str = Field(
            default="http://localhost:5005",
            description="Base URL of the local tools_server",
        )

    def __init__(self):
        self.valves = self.Valves()

    def get_streaming_availability(self, title: str, country: str = "us") -> str:
        """
        Get live streaming availability, service name, and price for a show or movie title.
        Use this for "live" questions such as where a title streams, in which country, or its
        price - not for questions about metadata already in the Netflix Shows knowledge base.

        :param title: The show or movie title to look up.
        :param country: Two-letter country code (default "us").
        :return: A human-readable summary of streaming options, or an error message.
        """
        try:
            resp = requests.get(
                f"{self.valves.server_url}/streaming",
                params={"title": title, "country": country},
                timeout=10,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            return f"Error calling tools_server: {exc}"

        data = resp.json()
        if "error" in data:
            return data["error"]
        return _format_options(data, country)
