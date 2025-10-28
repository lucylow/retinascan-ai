"""
Test script for RetinaScan AI API
"""
import requests
import json
from pathlib import Path
import sys


class APITester:
    """Test RetinaScan AI API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    def test_root(self):
        """Test root endpoint"""
        print("\n" + "="*60)
        print("Testing Root Endpoint")
        print("="*60)
        
        try:
            response = requests.get(f"{self.base_url}/")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            assert response.status_code == 200, "Root endpoint failed"
            self.results.append(("Root Endpoint", "PASS"))
            
        except Exception as e:
            print(f"Error: {str(e)}")
            self.results.append(("Root Endpoint", "FAIL"))
    
    def test_health(self):
        """Test health check endpoint"""
        print("\n" + "="*60)
        print("Testing Health Check Endpoint")
        print("="*60)
        
        try:
            response = requests.get(f"{self.base_url}/health")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            assert response.status_code == 200, "Health check failed"
            data = response.json()
            assert data["status"] == "healthy", "Server not healthy"
            assert "model_loaded" in data, "Model status missing"
            
            self.results.append(("Health Check", "PASS"))
            
        except Exception as e:
            print(f"Error: {str(e)}")
            self.results.append(("Health Check", "FAIL"))
    
    def test_model_info(self):
        """Test model info endpoint"""
        print("\n" + "="*60)
        print("Testing Model Info Endpoint")
        print("="*60)
        
        try:
            response = requests.get(f"{self.base_url}/model/info")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            assert response.status_code == 200, "Model info failed"
            self.results.append(("Model Info", "PASS"))
            
        except Exception as e:
            print(f"Error: {str(e)}")
            self.results.append(("Model Info", "FAIL"))
    
    def test_predict_no_file(self):
        """Test prediction endpoint without file"""
        print("\n" + "="*60)
        print("Testing Prediction Without File (Should Fail)")
        print("="*60)
        
        try:
            response = requests.post(f"{self.base_url}/predict")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            assert response.status_code == 422, "Should return validation error"
            self.results.append(("Predict No File", "PASS"))
            
        except Exception as e:
            print(f"Error: {str(e)}")
            self.results.append(("Predict No File", "FAIL"))
    
    def test_predict_with_sample(self, image_path: str = None):
        """Test prediction endpoint with sample image"""
        print("\n" + "="*60)
        print("Testing Prediction With Image")
        print("="*60)
        
        if not image_path or not Path(image_path).exists():
            print("No sample image provided or file not found")
            print("Skipping image prediction test")
            self.results.append(("Predict With Image", "SKIP"))
            return
        
        try:
            with open(image_path, "rb") as f:
                files = {"file": f}
                response = requests.post(f"{self.base_url}/predict", files=files)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                data = response.json()
                assert "severity_class" in data, "Missing severity_class"
                assert "confidence" in data, "Missing confidence"
                assert "label" in data, "Missing label"
                assert "recommendation" in data, "Missing recommendation"
                
                print(f"\nPrediction Results:")
                print(f"  Severity: {data['severity_level']} (Class {data['severity_class']})")
                print(f"  Confidence: {data['confidence']:.2%}")
                print(f"  Label: {data['label']}")
                
                self.results.append(("Predict With Image", "PASS"))
            else:
                print(f"Prediction failed with status {response.status_code}")
                self.results.append(("Predict With Image", "FAIL"))
            
        except Exception as e:
            print(f"Error: {str(e)}")
            self.results.append(("Predict With Image", "FAIL"))
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        for test_name, result in self.results:
            status_symbol = "✓" if result == "PASS" else "✗" if result == "FAIL" else "○"
            print(f"{status_symbol} {test_name}: {result}")
        
        passed = sum(1 for _, r in self.results if r == "PASS")
        failed = sum(1 for _, r in self.results if r == "FAIL")
        skipped = sum(1 for _, r in self.results if r == "SKIP")
        
        print(f"\nTotal: {len(self.results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
        print("="*60)


def main():
    """Main test function"""
    # Parse arguments
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    image_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("RetinaScan AI - API Test Suite")
    print(f"Base URL: {base_url}")
    if image_path:
        print(f"Sample Image: {image_path}")
    
    # Create tester
    tester = APITester(base_url)
    
    # Run tests
    tester.test_root()
    tester.test_health()
    tester.test_model_info()
    tester.test_predict_no_file()
    tester.test_predict_with_sample(image_path)
    
    # Print summary
    tester.print_summary()


if __name__ == "__main__":
    main()
