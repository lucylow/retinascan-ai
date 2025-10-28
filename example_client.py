"""
Example client for RetinaScan AI API
Demonstrates how to interact with the backend
"""
import requests
import json
from pathlib import Path
from typing import Dict, Optional


class RetinaScanClient:
    """Client for RetinaScan AI API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize client
        
        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict:
        """
        Check API health status
        
        Returns:
            Health status dictionary
        """
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def predict(self, image_path: str) -> Dict:
        """
        Predict diabetic retinopathy from retinal image
        
        Args:
            image_path: Path to retinal fundus image
            
        Returns:
            Prediction results dictionary
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = self.session.post(
                f"{self.base_url}/predict",
                files=files
            )
        
        response.raise_for_status()
        return response.json()
    
    def predict_batch(self, image_paths: list) -> list:
        """
        Predict multiple images
        
        Args:
            image_paths: List of image paths
            
        Returns:
            List of prediction results
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.predict(image_path)
                results.append({
                    'image': image_path,
                    'success': True,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'image': image_path,
                    'success': False,
                    'error': str(e)
                })
        return results
    
    def get_model_info(self) -> Dict:
        """
        Get model information
        
        Returns:
            Model information dictionary
        """
        response = self.session.get(f"{self.base_url}/model/info")
        response.raise_for_status()
        return response.json()
    
    def print_prediction(self, result: Dict):
        """
        Pretty print prediction results
        
        Args:
            result: Prediction result dictionary
        """
        print("\n" + "="*60)
        print("PREDICTION RESULTS")
        print("="*60)
        
        if not result.get('success', False):
            print(f"Error: {result.get('error', 'Unknown error')}")
            return
        
        print(f"Severity: {result['severity_level']} (Class {result['severity_class']})")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Label: {result['label']}")
        print(f"\nRecommendation:")
        print(f"  {result['recommendation']}")
        
        print(f"\nClass Probabilities:")
        for class_name, prob in result['class_probabilities'].items():
            print(f"  {class_name}: {prob:.2%}")
        
        print("="*60)


def example_single_prediction():
    """Example: Single image prediction"""
    print("\nExample 1: Single Image Prediction")
    print("-" * 60)
    
    # Initialize client
    client = RetinaScanClient("http://localhost:8000")
    
    # Check health
    health = client.health_check()
    print(f"API Status: {health['status']}")
    print(f"Model Loaded: {health['model_loaded']}")
    
    # Predict (replace with actual image path)
    image_path = "sample_retina.jpg"
    
    if Path(image_path).exists():
        result = client.predict(image_path)
        client.print_prediction(result)
    else:
        print(f"Sample image not found: {image_path}")
        print("Please provide a retinal fundus image to test")


def example_batch_prediction():
    """Example: Batch prediction"""
    print("\nExample 2: Batch Prediction")
    print("-" * 60)
    
    client = RetinaScanClient("http://localhost:8000")
    
    # List of images (replace with actual paths)
    image_paths = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg"
    ]
    
    # Filter existing images
    existing_images = [p for p in image_paths if Path(p).exists()]
    
    if not existing_images:
        print("No sample images found")
        return
    
    # Predict batch
    results = client.predict_batch(existing_images)
    
    # Print results
    for i, result in enumerate(results, 1):
        print(f"\nImage {i}: {result['image']}")
        if result['success']:
            print(f"  Severity: {result['result']['severity_level']}")
            print(f"  Confidence: {result['result']['confidence']:.2%}")
        else:
            print(f"  Error: {result['error']}")


def example_error_handling():
    """Example: Error handling"""
    print("\nExample 3: Error Handling")
    print("-" * 60)
    
    client = RetinaScanClient("http://localhost:8000")
    
    # Try to predict with non-existent file
    try:
        result = client.predict("nonexistent.jpg")
    except FileNotFoundError as e:
        print(f"Caught expected error: {e}")
    
    # Try to predict with invalid file
    # (This would return 400 from API)
    print("\nError handling examples demonstrated")


def example_model_info():
    """Example: Get model information"""
    print("\nExample 4: Model Information")
    print("-" * 60)
    
    client = RetinaScanClient("http://localhost:8000")
    
    info = client.get_model_info()
    print(json.dumps(info, indent=2))


def main():
    """Run all examples"""
    print("="*60)
    print("RetinaScan AI - Client Examples")
    print("="*60)
    
    try:
        example_single_prediction()
        example_batch_prediction()
        example_error_handling()
        example_model_info()
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API")
        print("Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()
