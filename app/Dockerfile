# Use Python 3.11 slim base image for consistency
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

# Copy the Streamlit application
COPY app/main_ui.py .

# Expose port 8501 for Streamlit
EXPOSE 8501

# Health check to ensure Streamlit is running
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the Streamlit application
CMD ["streamlit", "run", "main_ui.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--server.headless", "true"]
