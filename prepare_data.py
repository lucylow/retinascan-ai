"""
Data preparation script for APTOS 2019 Blindness Detection dataset
Downloads and organizes data for training
"""
import os
import shutil
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreparer:
    """Prepare APTOS dataset for training"""
    
    def __init__(self, source_dir: str, target_dir: str = "data/train"):
        """
        Initialize data preparer
        
        Args:
            source_dir: Directory containing downloaded APTOS images and CSV
            target_dir: Target directory for organized data
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.class_names = {
            0: "0_No_DR",
            1: "1_Mild",
            2: "2_Moderate",
            3: "3_Severe",
            4: "4_Proliferative"
        }
    
    def create_directories(self):
        """Create directory structure for organized data"""
        logger.info(f"Creating directory structure at {self.target_dir}")
        
        for class_id, class_name in self.class_names.items():
            class_dir = self.target_dir / class_name
            class_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {class_dir}")
    
    def organize_images(self, csv_file: str = "train.csv"):
        """
        Organize images into class directories based on CSV labels
        
        Args:
            csv_file: Name of CSV file with image labels
        """
        csv_path = self.source_dir / csv_file
        
        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_path}")
            return
        
        logger.info(f"Reading labels from {csv_path}")
        df = pd.read_csv(csv_path)
        
        logger.info(f"Total images: {len(df)}")
        logger.info(f"Class distribution:\n{df['diagnosis'].value_counts().sort_index()}")
        
        # Copy images to class directories
        copied = 0
        skipped = 0
        
        for idx, row in df.iterrows():
            image_id = row['id_code']
            diagnosis = row['diagnosis']
            
            # Find source image (try different extensions)
            source_image = None
            for ext in ['.png', '.jpg', '.jpeg']:
                candidate = self.source_dir / f"{image_id}{ext}"
                if candidate.exists():
                    source_image = candidate
                    break
            
            if source_image is None:
                logger.warning(f"Image not found: {image_id}")
                skipped += 1
                continue
            
            # Determine target directory
            class_name = self.class_names[diagnosis]
            target_image = self.target_dir / class_name / source_image.name
            
            # Copy image
            shutil.copy2(source_image, target_image)
            copied += 1
            
            if (idx + 1) % 100 == 0:
                logger.info(f"Processed {idx + 1}/{len(df)} images")
        
        logger.info(f"\nData organization complete!")
        logger.info(f"Copied: {copied} images")
        logger.info(f"Skipped: {skipped} images")
    
    def create_validation_split(self, val_ratio: float = 0.2):
        """
        Create validation split from training data
        
        Args:
            val_ratio: Fraction of data to use for validation
        """
        val_dir = self.target_dir.parent / "validation"
        logger.info(f"Creating validation split ({val_ratio:.0%}) at {val_dir}")
        
        for class_id, class_name in self.class_names.items():
            train_class_dir = self.target_dir / class_name
            val_class_dir = val_dir / class_name
            val_class_dir.mkdir(parents=True, exist_ok=True)
            
            # Get all images in class
            images = list(train_class_dir.glob("*"))
            num_val = int(len(images) * val_ratio)
            
            # Move validation images
            import random
            random.shuffle(images)
            val_images = images[:num_val]
            
            for img in val_images:
                shutil.move(str(img), str(val_class_dir / img.name))
            
            logger.info(f"{class_name}: {len(val_images)} validation images")
    
    def print_statistics(self):
        """Print dataset statistics"""
        logger.info("\n" + "="*60)
        logger.info("DATASET STATISTICS")
        logger.info("="*60)
        
        for split in ["train", "validation"]:
            split_dir = self.target_dir.parent / split
            if not split_dir.exists():
                continue
            
            logger.info(f"\n{split.upper()} SET:")
            total = 0
            
            for class_id, class_name in self.class_names.items():
                class_dir = split_dir / class_name
                if class_dir.exists():
                    count = len(list(class_dir.glob("*")))
                    total += count
                    logger.info(f"  {class_name}: {count} images")
            
            logger.info(f"  TOTAL: {total} images")


def download_instructions():
    """Print instructions for downloading APTOS dataset"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║         APTOS 2019 Blindness Detection Dataset                ║
    ╚════════════════════════════════════════════════════════════════╝
    
    To use this script, you need to download the dataset from Kaggle:
    
    1. Create a Kaggle account at https://www.kaggle.com
    
    2. Visit the competition page:
       https://www.kaggle.com/c/aptos2019-blindness-detection
    
    3. Download the following files:
       - train.csv
       - train_images.zip (or individual images)
    
    4. Extract to a directory, e.g., 'aptos_data/'
    
    5. Run this script:
       python prepare_data.py /path/to/aptos_data
    
    Alternative: Use Kaggle API
    
    1. Install: pip install kaggle
    
    2. Setup API credentials:
       https://github.com/Kaggle/kaggle-api#api-credentials
    
    3. Download dataset:
       kaggle competitions download -c aptos2019-blindness-detection
    
    4. Extract and run this script
    
    ╚════════════════════════════════════════════════════════════════╝
    """)


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        download_instructions()
        print("\nUsage: python prepare_data.py <source_directory>")
        print("Example: python prepare_data.py ./aptos_data")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    
    if not os.path.exists(source_dir):
        logger.error(f"Source directory not found: {source_dir}")
        sys.exit(1)
    
    # Create preparer
    preparer = DataPreparer(source_dir)
    
    # Organize data
    preparer.create_directories()
    preparer.organize_images()
    
    # Create validation split
    create_val = input("\nCreate validation split? (y/n): ").lower() == 'y'
    if create_val:
        preparer.create_validation_split()
    
    # Print statistics
    preparer.print_statistics()
    
    logger.info("\nData preparation complete!")
    logger.info("You can now train the model using train_model.py")


if __name__ == "__main__":
    main()
