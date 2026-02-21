#!/bin/bash

# PDF Genius Local Test (No Docker)
echo "🚀 Testing PDF Genius locally..."

# Check Python
echo "🐍 Checking Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Check Node.js
echo "🟢 Checking Node.js..."
node --version
if [ $? -ne 0 ]; then
    echo "⚠️  Node.js not found. Frontend will be limited."
fi

# Create virtual environment
echo "📦 Setting up Python virtual environment..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn pymupdf pdf2image pillow python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv httpx

# Create test environment
echo "⚙️  Creating test environment..."
cat > .env.test << EOF
DEBUG=true
SECRET_KEY=test-secret-key-change-in-production
DATABASE_URL=sqlite:///./test.db
STORAGE_TYPE=local
TEMP_DIR=/tmp/pdf_genius_test
USE_LOCAL_LLM=true
EOF

# Create test directory
mkdir -p /tmp/pdf_genius_test

# Start backend server
echo "🚀 Starting backend server..."
echo "Backend will run on: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload