# PulseGuard Scoring API — Cloud Run Dockerfile
# No sklearn, no xgboost — LightGBM native booster + numpy calibration only
FROM python:3.9-slim

WORKDIR /app

# LightGBM requires libgomp (OpenMP) — not present in slim base
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Copy model artifacts:
#   lgb_mono_champion.txt — native LightGBM booster (version-agnostic)
#   iso_x.npy, iso_y.npy — isotonic calibration lookup (numpy, no sklearn)
#   feature_medians.json  — training medians for 140-feature imputation
COPY outputs/models/ outputs/models/

# Cloud Run injects PORT env var; default to 8080
ENV PORT=8080
EXPOSE 8080

# Single worker — stateless, artifacts loaded once at startup
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
