# PulseGuard Scoring API — Cloud Run Dockerfile
# Python 3.9-slim base matches local dev environment
FROM python:3.9-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Copy model artifacts (pre-trained; not retrained in container)
COPY outputs/models/ outputs/models/

# Cloud Run injects PORT env var; default to 8080
ENV PORT=8080
EXPOSE 8080

# Single worker — stateless, artifacts loaded once at startup
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
