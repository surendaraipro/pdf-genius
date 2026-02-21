#!/bin/bash

# PDF Genius Railway Deployment Script
# Deploys to Railway.app in 15 minutes

set -e

echo "🚀 PDF Genius Railway Deployment"
echo "=========================================="

# Check for required tools
echo "🔍 Checking tools..."
command -v git >/dev/null 2>&1 || { echo "❌ Git is required"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "⚠️  npm not found, frontend build may fail"; }

# Check API keys
echo "🔑 Checking API keys..."
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ GROQ_API_KEY environment variable not set"
    echo "   Get it from: https://console.groq.com"
    exit 1
fi

if [ -z "$PDF_CO_API_KEY" ]; then
    echo "❌ PDF_CO_API_KEY environment variable not set"
    echo "   Get it from: https://apidocs.pdf.co"
    exit 1
fi

echo "✅ API keys found"

# Create Railway configuration
echo "📁 Creating Railway configuration..."

# railway.toml
cat > railway.toml << 'EOF'
[build]
builder = "nixpacks"
buildCommand = "echo 'Building PDF Genius...'"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 60
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3

[[services]]
name = "pdf-genius-backend"
sourcePath = "backend"
startCommand = "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 30

[[services]]
name = "pdf-genius-frontend"
sourcePath = "frontend"
startCommand = "cd frontend && npm run build && npm run start"
healthcheckPath = "/"
healthcheckTimeout = 30

[variables]
NODE_ENV = "production"
NEXT_PUBLIC_API_URL = "https://pdf-genius.up.railway.app"
EOF

# Create Railway environment variables
echo "⚙️  Creating environment variables..."

cat > railway.env << EOF
# Groq API
GROQ_API_KEY=$GROQ_API_KEY

# PDF.co API
PDF_CO_API_KEY=$PDF_CO_API_KEY

# Database (Railway will inject)
DATABASE_URL=\${{PostgreSQL.DATABASE_URL}}

# Redis (Railway will inject)
REDIS_URL=\${{Redis.REDIS_URL}}

# Security
SECRET_KEY=\${{RandomSecret 64}}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application
DEBUG=false
APP_NAME=PDF Genius
APP_VERSION=1.0.0
MAX_UPLOAD_SIZE_MB=100
RATE_LIMIT_PER_MINUTE=100
DOMAIN=https://pdf-genius.up.railway.app
ALLOWED_ORIGINS=https://pdf-genius.up.railway.app

# Storage (use local for now, add S3 later)
STORAGE_TYPE=local
TEMP_DIR=/tmp/pdf_genius

# Feature flags
ENABLE_AI_CHAT=true
ENABLE_PDF_PROCESSING=true
ENABLE_SUBSCRIPTIONS=true
EOF

# Create backend requirements.txt if missing
if [ ! -f "backend/requirements.txt" ]; then
    echo "📦 Creating backend requirements.txt..."
    cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pymupdf==1.23.8
pdf2image==1.16.3
pillow==10.1.0
python-multipart==0.0.6
sqlalchemy==2.0.23
alembic==1.13.1
psycopg2-binary==2.9.9
redis==5.0.1
rq==1.15.1
boto3==1.34.17
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.2
openai==1.6.1
EOF
fi

# Create frontend package.json if missing
if [ ! -f "frontend/package.json" ]; then
    echo "📦 Creating frontend package.json..."
    cat > frontend/package.json << 'EOF'
{
  "name": "pdf-genius-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.0.4",
    "react": "^18",
    "react-dom": "^18",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.0.0",
    "postcss": "^8.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "lucide-react": "^0.309.0",
    "@tanstack/react-query": "^5.12.2",
    "axios": "^1.6.2",
    "date-fns": "^3.0.0",
    "react-dropzone": "^14.2.3",
    "react-hook-form": "^7.48.2",
    "zod": "^3.22.4"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "eslint": "^8",
    "eslint-config-next": "14.0.4",
    "typescript": "^5"
  }
}
EOF
fi

# Create next.config.js for production
cat > frontend/next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://pdf-genius.up.railway.app',
  },
}

module.exports = nextConfig
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
lerna-debug.log*

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Railway
railway.env
EOF

echo "✅ Configuration files created"

# Initialize Git if not already
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: PDF Genius SaaS"
fi

echo ""
echo "🎉 PDF Genius is ready for Railway deployment!"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1. Create a Railway account (free):"
echo "   https://railway.app"
echo ""
echo "2. Install Railway CLI:"
echo "   npm i -g @railway/cli"
echo ""
echo "3. Login to Railway:"
echo "   railway login"
echo ""
echo "4. Create new project:"
echo "   railway init"
echo ""
echo "5. Add PostgreSQL database:"
echo "   railway add postgresql"
echo ""
echo "6. Add Redis:"
echo "   railway add redis"
echo ""
echo "7. Deploy:"
echo "   railway up"
echo ""
echo "8. Get your live URL:"
echo "   railway status"
echo ""
echo "⏱️  Estimated time: 15 minutes"
echo "💰 Cost: Free tier (PostgreSQL + Redis + Hosting)"
echo ""
echo "🚀 Your SaaS will be live at: https://pdf-genius.up.railway.app"
echo ""
echo "Need help? I can guide you through each step!"