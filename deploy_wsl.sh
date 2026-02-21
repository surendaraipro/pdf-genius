#!/bin/bash

# PDF Genius Deployment Script for WSL
# Run this in your WSL terminal

echo "🚀 PDF Genius Deployment from WSL"
echo "================================="

# Check if in correct directory
if [ ! -f "railway.toml" ]; then
    echo "❌ Not in PDF Genius directory"
    echo "Run: cd /home/surendar/.openclaw/workspace/pdf_genius"
    exit 1
fi

echo "✅ In PDF Genius directory: $(pwd)"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    echo "✅ Node.js installed"
fi

# Install Railway CLI
echo "📦 Installing Railway CLI..."
npm install -g @railway/cli

echo ""
echo "🎯 NEXT STEPS:"
echo ""
echo "1. Login to Railway:"
echo "   railway login"
echo "   (This opens your browser)"
echo ""
echo "2. Create project:"
echo "   railway init"
echo "   Choose: 'Create new project'"
echo "   Name: pdf-genius"
echo ""
echo "3. Add database:"
echo "   railway add postgresql"
echo ""
echo "4. Add Redis:"
echo "   railway add redis"
echo ""
echo "5. Set environment variables:"
echo "   railway variables set GROQ_API_KEY='YOUR_GROQ_API_KEY'"
echo "   railway variables set PDF_CO_API_KEY='YOUR_PDF_CO_API_KEY'"
echo "   railway variables set SECRET_KEY='\$(openssl rand -hex 32)'"
echo ""
echo "6. DEPLOY:"
echo "   railway up"
echo ""
echo "7. Get your URL:"
echo "   railway status"
echo ""
echo "⏱️  Time: 15-20 minutes"
echo "💰 Cost: Free"
echo "🌐 Your SaaS: https://pdf-genius.up.railway.app"
echo ""
echo "🚀 Ready? Start with: railway login"