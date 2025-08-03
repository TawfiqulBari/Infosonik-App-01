#!/bin/bash

# Production Deployment Script for Infosonik App
# This script ensures proper deployment with production configuration

echo "🚀 Starting production deployment..."

# Backup .env.prod file
if [ -f ".env.prod" ]; then
    echo "📋 Backing up .env.prod..."
    cp .env.prod .env.prod.backup
    echo "✅ .env.prod backed up"
else
    echo "⚠️  Warning: .env.prod not found"
fi

# Pull latest changes from GitHub
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Restore .env.prod file if it was overwritten
if [ -f ".env.prod.backup" ]; then
    echo "🔄 Restoring .env.prod..."
    mv .env.prod.backup .env.prod
    echo "✅ .env.prod restored"
fi

# Stop existing containers
echo "⏹️  Stopping existing containers..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod down

# Build and start containers with production configuration
echo "🏗️  Building and starting containers..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Wait a moment for containers to start
echo "⏳ Waiting for containers to start..."
sleep 10

# Check container status
echo "📊 Checking container status..."
docker-compose -f docker-compose.prod.yml ps

# Show recent logs
echo "📄 Recent application logs:"
docker-compose -f docker-compose.prod.yml logs app --tail=5

echo "✅ Deployment complete!"
echo "🌐 Application should be available at: https://infsnk-app-01.tawfiqulbari.work/"
