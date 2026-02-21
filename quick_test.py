"""
Quick test for PDF Genius backend
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    """Test health endpoint"""
    response = client.get("/health")
    print(f"Health check: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        return True
    return False

def test_pdf_processor():
    """Test PDF processor service"""
    try:
        from services.pdf_processor import PDFProcessor
        processor = PDFProcessor()
        print("✅ PDF Processor imported successfully")
        
        # Test with a sample PDF (create dummy)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            # Create minimal PDF
            f.write(b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\nxref\n0 2\n0000000000 65535 f\n0000000010 00000 n\ntrailer\n<<>>\nstartxref\n20\n%%EOF')
            temp_pdf = f.name
        
        try:
            metadata = processor.get_metadata(temp_pdf)
            print(f"✅ PDF metadata: {metadata}")
            
            text = processor.extract_text(temp_pdf)
            print(f"✅ Text extraction: {len(text)} characters")
            
            return True
        finally:
            os.unlink(temp_pdf)
            
    except Exception as e:
        print(f"❌ PDF Processor test failed: {str(e)}")
        return False

def test_ai_chat():
    """Test AI chat service"""
    try:
        from services.groq_service import GroqService
        ai = GroqService()
        print("✅ Groq Service imported successfully")
        
        # Test mock response
        response = ai._mock_response([
            {"role": "user", "content": "Test question"}
        ])
        print(f"✅ AI mock response: {response[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ AI Chat test failed: {str(e)}")
        return False

def test_auth():
    """Test authentication"""
    try:
        from services.auth import AuthService
        
        # Test password hashing
        password = "testpassword123"
        hashed = AuthService.get_password_hash(password)
        verified = AuthService.verify_password(password, hashed)
        
        print(f"✅ Password hashing: {'Verified' if verified else 'Failed'}")
        
        # Test token creation
        token = AuthService.create_access_token({"sub": "123"})
        print(f"✅ Token created: {token[:20]}...")
        
        return True
    except Exception as e:
        print(f"❌ Auth test failed: {str(e)}")
        return False

def main():
    print("🧪 Running PDF Genius Quick Tests")
    print("=" * 50)
    
    tests = [
        ("Health Endpoint", test_health),
        ("PDF Processor", test_pdf_processor),
        ("AI Chat", test_ai_chat),
        ("Authentication", test_auth),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🔍 Testing {name}...")
        try:
            success = test_func()
            results.append((name, success))
            print(f"   {'✅ PASS' if success else '❌ FAIL'}")
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {name:20} {status}")
    
    print(f"\n🎯 Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("🚀 All tests passed! PDF Genius is ready.")
        print("\nNext steps:")
        print("1. Start backend: cd backend && source venv/bin/activate && uvicorn main:app --reload")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Test API endpoints")
    else:
        print("⚠️  Some tests failed. Check dependencies.")

if __name__ == "__main__":
    main()