# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements-backend.txt requirements-frontend.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-backend.txt -r requirements-frontend.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p sessions chat

# Expose ports
EXPOSE 5000  # For Flask server
EXPOSE 8550  # For Flet UI

# Set environment variables
ENV FLASK_APP=server.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "server.py"]