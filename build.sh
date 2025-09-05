#!/bin/bash

# Berkeley Four Year Plan Generator - Production Build Script

set -e

echo "🚀 Building Berkeley Four Year Plan Generator for Production..."

# Create necessary directories
mkdir -p logs
mkdir -p ssl

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
pip install python-dotenv
cd ..

# Install Node.js dependencies and build frontend
echo "📦 Installing Node.js dependencies and building frontend..."
cd frontend
npm ci
npm run build
cd ..

# Create production environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating production environment file..."
    cp env.example .env
    echo "⚠️  Please update .env with your actual configuration values"
fi

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t berkeley-planner:latest .

echo "✅ Build completed successfully!"
echo ""
echo "To run the application:"
echo "  docker-compose up -d"
echo ""
echo "To run locally:"
echo "  cd backend && python app_production.py"
