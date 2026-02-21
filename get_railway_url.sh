#!/bin/bash

# Get Railway login URL

echo "🔗 Getting Railway login URL..."
echo "================================"

echo "Method 1: --print-url flag"
echo "---------------------------"
railway login --print-url 2>&1

echo ""
echo "Method 2: Generate token"
echo "------------------------"
railway token 2>&1

echo ""
echo "Method 3: Full output"
echo "---------------------"
railway login --browserless 2>&1 | grep -A5 -B5 "http"

echo ""
echo "💡 If no URL appears, try:"
echo "1. Check if Railway CLI is installed: railway --version"
echo "2. Update Railway: npm update -g @railway/cli"
echo "3. Try web dashboard: https://railway.app"
echo ""
echo "🎯 Or switch to Render.com (easier web interface)"