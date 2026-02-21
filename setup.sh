#!/bin/bash

# PDF Genius Setup Script
# Run this script to set up the development environment

set -e

echo "🚀 Setting up PDF Genius development environment..."

# Check for required tools
echo "🔍 Checking for required tools..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "⚠️  Node.js not found. Frontend development may be limited."; }

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p backend/storage
mkdir -p backend/alembic/versions
mkdir -p frontend/public

# Set up Python virtual environment for backend
echo "🐍 Setting up Python virtual environment..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Initialize Alembic
echo "🗄️  Setting up database migrations..."
if [ ! -f "alembic/versions" ]; then
    alembic init alembic
fi

# Generate initial migration
if [ ! -f "alembic/versions/initial_migration.py" ]; then
    alembic revision --autogenerate -m "Initial migration"
fi

cd ..

# Set up Node.js for frontend
echo "🟢 Setting up Node.js environment..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

# Create environment files
echo "⚙️  Creating environment files..."

# Backend .env
cat > backend/.env << EOF
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/pdf_genius

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=development-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Storage
STORAGE_TYPE=local
TEMP_DIR=/tmp/pdf_genius

# AI Services
OPENAI_API_KEY=your-openai-api-key-here
USE_LOCAL_LLM=true
LOCAL_LLM_MODEL=Qwen/Qwen2.5-7B-Instruct

# Stripe (optional)
STRIPE_SECRET_KEY=your-stripe-secret-key-here
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret-here

# Application
DEBUG=true
APP_NAME=PDF Genius
APP_VERSION=0.1.0
MAX_UPLOAD_SIZE_MB=100
RATE_LIMIT_PER_MINUTE=60
EOF

# Frontend .env.local
cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=PDF Genius
NEXT_PUBLIC_APP_VERSION=0.1.0
EOF

echo "✅ Environment files created."

# Start services with Docker Compose
echo "🐳 Starting services with Docker Compose..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ All services are running!"
else
    echo "⚠️  Some services may not be running. Check with 'docker-compose ps'"
fi

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec backend alembic upgrade head

echo ""
echo "🎉 PDF Genius setup complete!"
echo ""
echo "📊 Services:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   PostgreSQL: localhost:5432"
echo "   Redis: localhost:6379"
echo ""
echo "🚀 Quick start:"
echo "   1. Visit http://localhost:3000"
echo "   2. Upload a PDF file"
echo "   3. Try the AI chat feature"
echo ""
echo "🛠️  Development commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • Restart services: docker-compose restart"
echo "   • Rebuild: docker-compose up --build"
echo ""
echo "📝 Next steps:"
echo "   1. Add your OpenAI API key to backend/.env for AI features"
echo "   2. Configure Stripe for payments (optional)"
echo "   3. Set up production deployment"
echo ""
echo "Happy coding! 🚀"