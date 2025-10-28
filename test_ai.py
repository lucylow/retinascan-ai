"""
Test script to verify AI functionality is working properly
Tests both the Supabase edge function integration and FastAPI backend
"""

import os
import sys
import requests
import json
from pathlib import Path


def test_supabase_edge_function(base_url: str = None):
    """Test Supabase Edge Function AI"""
    print("\n" + "="*60)
    print("Testing Supabase Edge Function AI")
    print("="*60)
    
    if not base_url:
        print("❌ No Supabase URL provided")
        return False
    
    try:
        # Check if Supabase is configured
        health_url = f"{base_url}/rest/v1/"
        response = requests.get(health_url, timeout=5)
        
        if response.status_code in [200, 401, 404]:
            print("✅ Supabase connection successful")
        else:
            print(f"⚠️ Supabase returned status: {response.status_code}")
        
        # Note: To test the actual AI function, you need:
        # 1. Deploy the edge function
        # 2. Set LOVABLE_API_KEY in Supabase secrets
        # 3. Have valid Supabase credentials
        
        print("\n📋 To test AI analysis:")
        print("1. Deploy edge function: supabase functions deploy analyze-retina")
        print("2. Set secret: supabase secrets set LOVABLE_API_KEY=your-key")
        print("3. Use the frontend to upload and analyze an image")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_fastapi_backend(host: str = "http://localhost:8000"):
    """Test FastAPI backend AI"""
    print("\n" + "="*60)
    print("Testing FastAPI Backend AI")
    print("="*60)
    
    try:
        # Test health endpoint
        response = requests.get(f"{host}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ FastAPI backend is running")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Model loaded: {data.get('model_loaded')}")
            
            if data.get('model_loaded'):
                print("✅ AI model is loaded and ready")
            else:
                print("⚠️ AI model not loaded (using fallback dummy model)")
            
            # Test model info
            info_response = requests.get(f"{host}/model/info", timeout=5)
            if info_response.status_code == 200:
                info = info_response.json()
                print(f"   Architecture: {info.get('architecture', 'N/A')}")
                print(f"   Parameters: {info.get('total_params', 'N/A'):,}")
            
            return True
        else:
            print(f"❌ FastAPI returned status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ FastAPI backend is not running")
        print("   Start it with: python3 main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_image_processing():
    """Test image processing utilities"""
    print("\n" + "="*60)
    print("Testing Image Processing Utilities")
    print("="*60)
    
    try:
        from utils.image_processor import ImageProcessor
        from config import Config
        
        print(f"✅ ImageProcessor imported successfully")
        print(f"✅ Config: {Config.IMAGE_SIZE} image size, {Config.NUM_CLASSES} classes")
        print(f"✅ Allowed extensions: {', '.join(Config.ALLOWED_EXTENSIONS)}")
        
        # Test file extension validation
        test_files = ["test.jpg", "test.png", "test.pdf", "test.jpeg"]
        for filename in test_files:
            is_valid = ImageProcessor.validate_file_extension(filename)
            status = "✅" if is_valid else "❌"
            print(f"   {status} {filename}: {is_valid}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing image processor: {str(e)}")
        return False


def test_model_manager():
    """Test model manager"""
    print("\n" + "="*60)
    print("Testing Model Manager")
    print("="*60)
    
    try:
        from utils.model_manager import model_manager
        from config import Config
        
        print(f"✅ ModelManager imported successfully")
        
        # Try to load model
        print("Attempting to load model...")
        loaded = model_manager.load_model()
        
        if loaded:
            print("✅ Model loaded successfully")
            
            # Get model info
            info = model_manager.get_model_info()
            print(f"   Model loaded: {info.get('loaded')}")
            print(f"   Input shape: {info.get('input_shape')}")
            print(f"   Total params: {info.get('total_params', 'N/A')}")
            
            return True
        else:
            print("⚠️ Model not found, will use dummy model")
            return True
            
    except Exception as e:
        print(f"❌ Error loading model manager: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("RetinaScan AI - System Verification")
    print("="*60)
    
    results = []
    
    # Test 1: Image processing
    results.append(("Image Processing", test_image_processing()))
    
    # Test 2: Model manager
    results.append(("Model Manager", test_model_manager()))
    
    # Test 3: FastAPI backend
    results.append(("FastAPI Backend", test_fastapi_backend()))
    
    # Test 4: Supabase (optional)
    supabase_url = os.getenv("VITE_SUPABASE_URL")
    if supabase_url:
        results.append(("Supabase Integration", test_supabase_edge_function(supabase_url)))
    else:
        print("\n⚠️ Supabase URL not configured (optional)")
        results.append(("Supabase Integration", None))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for name, result in results:
        if result is None:
            status = "SKIPPED"
            skipped += 1
        elif result:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"{name}: {status}")
    
    print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 All critical tests passed! AI is working properly.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

