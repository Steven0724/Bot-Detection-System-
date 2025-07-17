# Professional Traffic Analyzer - Docker Container
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies for matplotlib and data processing
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    pkg-config \
    libfreetype6-dev \
    libpng-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p /app/output /app/logs /app/data/samples

# Create a sample log file for testing if none exists
RUN echo '192.168.1.100 - US - [01/07/2025:06:00:01] "GET /admin/login HTTP/1.1" 404 1234 "-" "curl/7.68.0" 150' > /app/data/samples/sample.log && \
    echo '203.0.113.1 - NO - [01/07/2025:06:00:02] "GET /index.html HTTP/1.1" 200 5678 "-" "Mozilla/5.0" 300' >> /app/data/samples/sample.log && \
    echo '192.168.1.101 - US - [01/07/2025:06:00:03] "POST /.env HTTP/1.1" 404 1234 "-" "python-requests/2.28.1" 124' >> /app/data/samples/sample.log

# Set proper permissions
RUN chmod -R 755 /app

# Create non-root user for security
RUN groupadd -r analyzer && useradd -r -g analyzer analyzer
RUN chown -R analyzer:analyzer /app
USER analyzer

# Set the default entry point
ENTRYPOINT ["python", "src/main_analyzer.py"]

# Default command shows help
CMD ["--help"]

# Metadata labels
LABEL maintainer="Traffic Analyzer Team" \
      version="2.0" \
      description="Professional bot detection and traffic analysis system"
     
