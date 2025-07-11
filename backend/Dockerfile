# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for PostgreSQL and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add additional production dependencies
RUN pip install --no-cache-dir \
    asyncpg==0.29.0 \
    psycopg2-binary==2.9.9

# Copy the application code
COPY . .

# Create a non-root user to run the application
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Copy entrypoint script
COPY docker-entrypoint.sh /app/
COPY mark_migration_complete.py /app/

# Make the entrypoint script executable
USER root
RUN chmod +x /app/docker-entrypoint.sh && \
    apt-get update && apt-get install -y netcat-traditional && \
    rm -rf /var/lib/apt/lists/*
USER appuser

# Set the entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]