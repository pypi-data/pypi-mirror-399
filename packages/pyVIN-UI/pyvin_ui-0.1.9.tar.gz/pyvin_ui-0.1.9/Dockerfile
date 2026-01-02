# Multi-stage Dockerfile for pyVIN
# Stage 1: Builder - Install dependencies and run tests
FROM python:3.14-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/

# Run tests (optional - comment out for faster builds)
# RUN pip install -e ".[dev]" && pytest

# Stage 2: Runtime - Minimal production image
FROM python:3.14-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Create non-root user
RUN useradd -m -u 1000 pyvin && \
    mkdir -p /app && \
    chown -R pyvin:pyvin /app

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application files
COPY --chown=pyvin:pyvin src/ ./src/
COPY --chown=pyvin:pyvin pyproject.toml ./

# Switch to non-root user
USER pyvin

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health')"

# Run Streamlit app
CMD ["streamlit", "run", "src/ui/app.py"]
