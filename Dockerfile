# BookBot - Professional Text Analysis Tool
# Multi-stage build for minimal image size

# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.12-slim

LABEL maintainer="David Benito Campo"
LABEL description="BookBot - Professional Text Analysis Tool"
LABEL version="1.0.0"

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash bookbot

WORKDIR /app

# Install runtime dependencies for matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6 \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/bookbot/.local

# Copy application code
COPY --chown=bookbot:bookbot . .

# Set user
USER bookbot

# Add local bin to PATH
ENV PATH=/home/bookbot/.local/bin:$PATH

# Set Python to run unbuffered for better logging
ENV PYTHONUNBUFFERED=1

# Default command - show help
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
