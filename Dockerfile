# Use a small base image
FROM python:3.13-slim

# Set non-root user (optional but good)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a working dir
WORKDIR /app

# Install system deps needed for common packages (keep minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
 && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code (only what we need)
COPY app_api.py .
COPY models/ models/    

EXPOSE 7860

# Use a lightweight command; uvicorn is fine
CMD ["uvicorn", "app_api:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
