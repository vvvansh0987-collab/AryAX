#!/bin/bash
# Setup script for AryaX Platform

set -e

echo "🚀 AryaX Platform - Setup Script"
echo "=================================="

# Check Python version
echo "✓ Checking Python version..."
python --version

# Create virtual environment (optional)
if [ ! -d "venv" ]; then
    echo "✓ Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
fi

# Install dependencies
echo "✓ Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Copy environment file
if [ ! -f ".env" ]; then
    echo "✓ Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Create necessary directories
echo "✓ Creating directories..."
mkdir -p alembic/versions
mkdir -p k8s
mkdir -p logs

# Run database migrations
echo "✓ Running database migrations..."
alembic upgrade head

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your configuration"
echo "2. Start services: docker-compose up -d"
echo "3. Run development server: python run.py"
echo "4. Visit http://localhost:8000/docs for API documentation"
