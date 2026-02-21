#!/usr/bin/env python3
"""
Test LLM Router with multiple providers
"""

import asyncio
import os
from backend.services.llm_router import llm_router

async def test_llm_router():
    """Test the LLM router"""
    print("🤖 Testing LLM Router...")
    print("=" * 50)
    
    # Check available providers
    providers = llm_router.get_available_providers()
    print(f"📋 Available providers: {len(providers)}")
    for provider in providers:
        print(f"  • {provider['name']}: {provider['description']}")
    
    print("\n🧪 Testing chat completion...")
    
    # Test messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    try:
        result = await llm_router.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=100
        )
        
        print(f"\n✅ Result from {result['provider']}:")
        print(f"Response: {result['response'][:100]}...")
        print(f"Success: {result['success']}")
        print(f"Description: {result.get('description', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n📊 Router stats:")
    stats = llm_router.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    # Set environment variables for testing
    os.environ["GROQ_API_KEY"] = "YOUR_GROQ_API_KEY"
    os.environ["PDF_CO_API_KEY"] = "YOUR_PDF_CO_API_KEY"
    
    asyncio.run(test_llm_router())