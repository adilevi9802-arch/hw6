# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Keep Python output unbuffered and skip .pyc files for cleaner container logs.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first so this layer is cached across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application package and WSGI entrypoint.
COPY app ./app
COPY wsgi.py .

EXPOSE 5005

# Serve with gunicorn (a production WSGI server) rather than Flask's dev server.
CMD ["gunicorn", "--bind", "0.0.0.0:5005", "--workers", "2", "wsgi:app"]
