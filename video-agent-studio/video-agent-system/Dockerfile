# Production Dockerfile for Video Agent System (FastAPI + FastMCP + Web UI)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including FFmpeg and fonts for subtitle/image rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    curl \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure workspace directories exist
RUN mkdir -p workspace/input workspace/output workspace/temp

# Expose default port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Healthcheck monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT}/mcp_healthcheck || exit 1

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
