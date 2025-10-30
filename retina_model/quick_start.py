"""
Quick Start Script for RetinaScan AI Model
Run this to start training immediately
"""

import subprocess
import sys


def install_requirements():
    """Install required packages"""

    requirements = [
        "tensorflow==2.13.0",
        "opencv-python==4.8.1.78",
        "numpy==1.24.3",
        "pandas==2.0.3",
        "matplotlib==3.7.2",
        "scikit-learn==1.3.0",
        "albumentations==1.3.1",
        "Pillow==10.0.0"
    ]

    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")


def quick_train():
    """Quick training with sample data"""

    from .train_model import RetinaModelTrainer

    config = {
        'data_csv_path': 'data/sample_data.csv',
        'img_size': (224, 224),
        'batch_size': 16,
        'epochs': 10,
        'learning_rate': 0.001,
        'use_pretrained': True
    }

    trainer = RetinaModelTrainer(config)
    history, results = trainer.train()

    return results


if __name__ == "__main__":
    print("🚀 RetinaScan AI Quick Start")
    print("1. Installing requirements...")
    install_requirements()

    print("\n2. Starting quick training...")
    print("Note: You'll need to provide your dataset in 'data/sample_data.csv'")
    print("Format: image_path,diagnosis")

    try:
        results = quick_train()
        print("\n✅ Training completed!")
        print(f"Final Accuracy: {results['test_accuracy']:.4f}")
    except Exception as e:
        print(f"\n❌ Training failed: {str(e)}")
        print("Please ensure you have the dataset prepared.")


