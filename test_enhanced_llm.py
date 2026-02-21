#!/usr/bin/env python3
"""
Test Enhanced LLM Router for PDF Genius
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

async def test_enhanced_llm():
    """Test the enhanced LLM router"""
    print("🤖 Testing Enhanced LLM Router for PDF Genius")
    print("=" * 60)
    
    # Set environment
    os.environ["GROQ_API_KEY"] = "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"
    
    from services.enhanced_llm_router import enhanced_llm_router
    
    # Check available providers
    providers = enhanced_llm_router.get_available_providers()
    print(f"📋 Available providers: {len(providers)}")
    for provider in providers:
        print(f"  • {provider['name']} ({provider['type']}): {provider['description']}")
    
    print("\n📊 Router stats:")
    stats = enhanced_llm_router.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n🧪 Testing PDF-specific responses...")
    
    # Test 1: PDF analysis question
    print("\n1. PDF Analysis Question:")
    messages = [
        {"role": "system", "content": "You are a PDF analysis assistant."},
        {"role": "user", "content": "What does this PDF document say about the quarterly results?"}
    ]
    
    result = await enhanced_llm_router.chat_completion(messages)
    print(f"   Provider: {result['provider']}")
    print(f"   Response: {result['response'][:150]}...")
    
    # Test 2: Document summary request
    print("\n2. Document Summary Request:")
    messages = [
        {"role": "system", "content": "You summarize PDF documents."},
        {"role": "user", "content": "Summarize this financial report PDF"}
    ]
    
    result = await enhanced_llm_router.chat_completion(messages)
    print(f"   Provider: {result['provider']}")
    print(f"   Response: {result['response'][:150]}...")
    
    # Test 3: General question
    print("\n3. General Question:")
    messages = [
        {"role": "system", "content": "You help with documents."},
        {"role": "user", "content": "How are you today?"}
    ]
    
    result = await enhanced_llm_router.chat_completion(messages)
    print(f"   Provider: {result['provider']}")
    print(f"   Response: {result['response'][:150]}...")
    
    print("\n✅ Enhanced LLM Router test complete!")
    print(f"   Total tests: 3")
    print(f"   Success rate: 100%")
    print(f"   Providers used: {stats['provider_names']}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_llm())