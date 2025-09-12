#!/bin/bash

# CloneGallery Deployment Script
# This script sets up and deploys the CloneGallery application

set -e

echo "🚀 Starting CloneGallery deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data models uploads

# Set permissions
chmod 755 data models uploads

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service health..."

# Check web service
if curl -f http://localhost:3000/health > /dev/null 2>&1; then
    echo "✅ Web service is running on http://localhost:3000"
else
    echo "⚠️  Web service may not be ready yet"
fi

# Check API service
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API service is running on http://localhost:8000"
else
    echo "⚠️  API service may not be ready yet"
fi

# Initialize database
echo "🗄️  Initializing database..."
docker-compose run --rm db-migrate
docker-compose run --rm db-seed

echo "🎉 Deployment complete!"
echo ""
echo "📋 Service URLs:"
echo "   Frontend: http://localhost:3000"
echo "   API:      http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🔧 Management Commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop all:     docker-compose down"
echo "   Restart:      docker-compose restart"
echo "   Update:       docker-compose pull && docker-compose up -d"
echo ""
echo "📊 Demo Accounts:"
echo "   Admin:  admin@clonegallery.local"
echo "   Editor: editor@clonegallery.local"
echo "   User:   user@clonegallery.local"
echo ""
echo "🎨 Features Available:"
echo "   ✅ Image upload with editing (crop, resize, filters)"
echo "   ✅ AI image generation"
echo "   ✅ One-like-per-user system"
echo "   ✅ Database persistence"
echo "   ✅ Responsive design"
