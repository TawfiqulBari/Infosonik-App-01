#!/bin/bash

# Deployment script to fix gateway timeout issues
# This script applies the fixes for database connection and timeout issues

echo "🚀 Starting deployment with fixes for gateway timeout issues..."

# Stop existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Remove existing containers and images to ensure clean rebuild
echo "Cleaning up old containers and images..."
docker system prune -f
docker volume prune -f

# Rebuild and start services
echo "Rebuilding and starting services..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 30

# Check service status
echo "Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# Check logs for any issues
echo "Checking application logs..."
docker-compose -f docker-compose.prod.yml logs app

echo "✅ Deployment completed!"
echo "🌐 Your application should now be available at: https://infsnk-app-01.tawfiqulbari.work/"
echo ""
echo "🔍 If you still experience issues, check the logs with:"
echo "   docker-compose -f docker-compose.prod.yml logs -f app"