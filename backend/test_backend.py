"""
Simple test script for Flask backend API
Run this after starting the Flask server to test endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("Testing /api/health...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_model_info():
    """Test model info endpoint"""
    print("Testing /api/model/info...")
    response = requests.get(f"{BASE_URL}/api/model/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_diagnosis_info():
    """Test diagnosis info endpoint"""
    print("Testing /api/diagnosis/info...")
    response = requests.get(f"{BASE_URL}/api/diagnosis/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_predict(image_path):
    """Test prediction endpoint"""
    print(f"Testing /api/predict with {image_path}...")
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{BASE_URL}/api/predict", files=files)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except FileNotFoundError:
        print(f"Image file not found: {image_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("RetinaScan AI Flask Backend - API Tests")
    print("=" * 50)
    print()
    
    # Test endpoints
    test_health()
    test_model_info()
    test_diagnosis_info()
    
    # Test prediction (uncomment if you have a test image)
    # test_predict("path/to/test_image.jpg")
    
    print("=" * 50)
    print("Testing complete!")
    print("=" * 50)

