#!/bin/bash

# Development setup script for Conciergerie Cordo

set -e

echo "🚀 Setting up Conciergerie Cordo development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing."
    echo "   At minimum, you need to set:"
    echo "   - STRIPE_PUBLISHABLE_KEY"
    echo "   - STRIPE_SECRET_KEY"
    echo "   - SECRET_KEY"
    echo ""
    read -p "Press Enter when you have configured .env file..."
fi

# Start Docker containers
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec web flask db upgrade

# Seed initial data
echo "🌱 Seeding initial data..."
docker-compose exec web python seed_data.py

echo ""
echo "✅ Development environment is ready!"
echo ""
echo "🌐 Application: http://localhost:5000"
echo "🗄️  Database: localhost:5432 (postgres/postgres)"
echo ""
echo "📝 Useful commands:"
echo "   docker-compose logs web          # View application logs"
echo "   docker-compose exec web bash     # Access container shell"
echo "   docker-compose down              # Stop containers"
echo "   docker-compose up                # Start containers (foreground)"
echo ""
echo "Happy coding! 🎉"