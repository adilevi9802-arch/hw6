"""HTTP routes for the tools server.

Routes are declared inside a factory function that closes over the injected
configuration, so no global mutable state is required. This keeps the module
functional and makes each route trivially testable with a custom config.
"""
from __future__ import annotations

from typing import Mapping

from flask import Blueprint, jsonify, request

from .rapidapi_client import UpstreamError, fetch_streaming_availability


def create_blueprint(config: Mapping[str, object]) -> Blueprint:
    """Create the API blueprint bound to a specific configuration.

    Args:
        config: The application configuration mapping.

    Returns:
        Blueprint: A Flask blueprint exposing the /health and /streaming routes.
    """
    bp = Blueprint("api", __name__)

    @bp.get("/health")
    def health():
        """Liveness probe.

        Returns:
            Response: JSON ``{"status": "ok"}`` with HTTP 200.
        """
        return jsonify(status="ok")

    @bp.get("/streaming")
    def streaming():
        """Return live streaming availability for a title.

        Query params:
            title: (required) the title to look up.
            country: (optional) two-letter country code; falls back to the
                configured default country.

        Returns:
            Response: JSON with the title, country and streamingOptions on
            success, or a JSON ``{"error": ...}`` with an appropriate status
            code on failure.
        """
        title = request.args.get("title", "").strip()
        country = request.args.get(
            "country", str(config["default_country"])
        ).lower()

        if not title:
            return jsonify(error="query param 'title' is required"), 400

        try:
            result = fetch_streaming_availability(config, title, country)
        except UpstreamError as exc:
            return jsonify(error=str(exc)), exc.status_code

        return jsonify(result)

    return bp
