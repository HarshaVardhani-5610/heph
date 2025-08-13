# Use Python 3.12 Alpine base image
FROM python:3.12-alpine

# Install system dependencies
RUN apk add --no-cache \
    git \
    bash \
    curl \
    build-base \
    linux-headers

# Set working directory
WORKDIR /workspaces/heph

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN addgroup -g $USER_GID $USERNAME && \
    adduser -D -u $USER_UID -G $USERNAME $USERNAME

# Set the default user
USER $USERNAME

# Expose ports for Streamlit and other services
EXPOSE 8501 8000
