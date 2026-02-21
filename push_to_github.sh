#!/bin/bash

# Push PDF Genius to GitHub
# Run this script, then enter your GitHub credentials when prompted

echo "🚀 Pushing PDF Genius to GitHub..."
echo "================================="

# Check if in correct directory
if [ ! -f "render.yaml" ]; then
    echo "❌ Not in PDF Genius directory"
    echo "Run: cd /home/surendar/.openclaw/workspace/pdf_genius"
    exit 1
fi

echo "✅ In PDF Genius directory: $(pwd)"

# Check git status
echo "📊 Git status:"
git status --short

# Add remote if not already added
if ! git remote | grep -q origin; then
    echo "🔗 Adding GitHub remote..."
    git remote add origin https://github.com/surendaraipro/pdf-genius.git
fi

echo ""
echo "🎯 READY TO PUSH!"
echo ""
echo "Run this command:"
echo "  git push -u origin main"
echo ""
echo "You'll be prompted for:"
echo "  Username: your GitHub username"
echo "  Password: your GitHub password OR Personal Access Token"
echo ""
echo "💡 If you have 2FA enabled, use a Personal Access Token:"
echo "   https://github.com/settings/tokens"
echo ""
echo "🚀 After pushing, go to: https://render.com"
echo "   Sign up with GitHub → New Blueprint → Connect repo → Deploy!"