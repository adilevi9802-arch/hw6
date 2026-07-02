"""WSGI entrypoint for the tools server.

In production the app is served by gunicorn as ``wsgi:app``. Running this file
directly starts Flask's built-in server, which is convenient for local
development only.
"""
from __future__ import annotations

from app import create_app

# The WSGI callable that gunicorn imports (``gunicorn wsgi:app``).
app = create_app()


if __name__ == "__main__":
    # Development-only server. Binds to all interfaces so it is reachable
    # from outside a container. Use gunicorn for anything production-like.
    app.run(host="0.0.0.0", port=5005)
