#!/bin/bash

# Berkeley Four Year Plan Generator - Production Startup Script

set -e

echo "🚀 Starting Berkeley Four Year Plan Generator in Production Mode..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Creating from template..."
    cp env.example .env
    echo "⚠️  Please update .env with your actual configuration values before running again"
    exit 1
fi

# Load environment variables
source .env

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY not set in .env file"
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p ssl

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt

# Install Node.js dependencies and build frontend
echo "📦 Building frontend..."
cd frontend
npm ci
npm run build
cd ..

# Start the production backend
echo "🚀 Starting production backend..."
cd backend
python app_production.py
