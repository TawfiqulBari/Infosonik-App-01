# Multi-stage build for React frontend and FastAPI backend

# Stage 1: Build React frontend
FROM node:18-alpine as frontend-build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY src/ ./src/
COPY public/ ./public/
RUN npm run build

# Stage 2: Build Python backend
FROM python:3.11-slim as backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application
COPY main.py .

# Copy built React frontend from first stage
COPY --from=frontend-build /app/build ./static

# Create a script to serve both frontend and API
RUN echo '#!/bin/bash\nuvicorn main:app --host 0.0.0.0 --port 8000' > start.sh
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Run the application
CMD ["./start.sh"]
