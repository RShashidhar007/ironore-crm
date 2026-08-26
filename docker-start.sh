#!/bin/bash
# Docker Quick Start Script for IronOre CRM

set -e

echo "================================"
echo "IronOre CRM - Docker Setup"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    echo "Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Desktop."
    exit 1
fi

echo "✓ Docker detected"
echo "✓ Docker Compose detected"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📋 Creating .env from .env.docker template..."
    cp .env.docker .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Review and update .env with your configuration:"
    echo "   - SA_PASSWORD: SQL Server password"
    echo "   - SECRET_KEY: Generate a secure key"
    echo "   - SMTP settings: Configure email"
    echo ""
    read -p "Press Enter after updating .env..."
fi

echo ""
echo "🏗️  Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✓ Services are running!"
echo ""
echo "🌐 Access points:"
echo "   • Frontend: http://localhost"
echo "   • API: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • Database: localhost:1433"
echo ""
echo "📝 Useful commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • View specific service: docker-compose logs -f backend"
echo ""
