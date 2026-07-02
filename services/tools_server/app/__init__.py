"""Application factory for the tools server.

Exposes :func:`create_app`, a functional factory that builds a fully wired
Flask application. Using a factory (instead of a module-level app) keeps
configuration explicit and lets tests build isolated app instances.
"""
from __future__ import annotations

from flask import Flask

from .config import load_config
from .routes import create_blueprint


def create_app() -> Flask:
    """Build and configure the Flask application.

    Returns:
        Flask: A ready-to-serve Flask application with routes registered.
    """
    app = Flask(__name__)
    config = load_config()
    app.register_blueprint(create_blueprint(config))
    return app
