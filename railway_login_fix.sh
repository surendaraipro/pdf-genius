#!/bin/bash

# Fix for Railway login issue

echo "🔧 Fixing Railway login..."
echo "=========================="

# Method 1: Try with --yes flag
echo "1. Trying railway login --yes..."
railway login --yes 2>&1 | head -20

echo ""
echo "If that didn't work, try:"
echo ""
echo "2. Manual browser login:"
echo "   railway login --browserless"
echo "   (Then open the URL in your browser)"
echo ""
echo "3. Or set environment variable:"
echo "   RAILWAY_TELEMETRY_OPT_IN=true railway login"
echo ""
echo "4. Alternative: Skip telemetry prompt:"
echo "   export RAILWAY_NO_TELEMETRY=1"
echo "   railway login"
echo ""
echo "💡 The prompt expects 'Y' (capital) or Enter (default is Y)"
echo "   If it exits too fast, use one of the methods above."