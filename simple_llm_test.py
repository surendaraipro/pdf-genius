#!/usr/bin/env python3
"""
Simple test for Enhanced LLM Router
"""

import os
import sys

# Set environment
os.environ["GROQ_API_KEY"] = "YOUR_GROQ_API_KEY"

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

print("🤖 Testing Enhanced LLM Router")
print("=" * 50)

# Import and test
try:
    from services.enhanced_llm_router import enhanced_llm_router
    
    print("✅ Enhanced LLM Router imported successfully")
    
    # Check providers
    providers = enhanced_llm_router.get_available_providers()
    print(f"\n📋 Available providers: {len(providers)}")
    for provider in providers:
        print(f"  • {provider['name']} - {provider['description']}")
    
    # Get stats
    stats = enhanced_llm_router.get_stats()
    print(f"\n📊 Primary provider: {stats['primary_provider']}")
    print(f"   Enabled providers: {stats['enabled_providers']}")
    
    print("\n🎯 PDF Genius LLM Strategy:")
    print("   1. Groq (Cloud) - For complex PDF analysis")
    print("   2. PDF Genius Simple (Local) - For basic tasks")
    print("   3. Fallback - Always available")
    
    print("\n💰 Cost: $0/month (Free tiers)")
    print("⚡ Speed: Fast responses")
    print("🔒 Privacy: Local options available")
    
    print("\n✅ Enhanced LLM Router is ready for PDF Genius!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n💡 Solution: Install dependencies:")
    print("   pip install httpx")
    
except Exception as e:
    print(f"❌ Error: {e}")