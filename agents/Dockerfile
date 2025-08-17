# Use Python 3.11 slim base image for smaller footprint
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application and dependencies
COPY agents/main_service.py .
COPY api_key_manager.py .
COPY .env .env

# Expose port 8000 for the FastAPI service
EXPOSE 8000

# Health check to ensure service is running
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application using uvicorn
CMD ["uvicorn", "main_service:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
