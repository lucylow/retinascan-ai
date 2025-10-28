"""
Enhanced image processing utilities for retinal fundus images
Improvements:
- Ben Graham preprocessing (state-of-the-art for retinal images)
- Green channel extraction
- Advanced circular cropping
- Improved quality assessment
- Better preprocessing pipeline
"""
import numpy as np
import cv2
from PIL import Image, ImageEnhance
import io
from typing import Union, Tuple
from config import Config

# Import for image quality assessment
import tensorflow as tf
from io import BytesIO


class ImageProcessor:
    """Enhanced preprocessing and enhancement of retinal fundus images"""
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """
        Validate if file has an allowed extension
        
        Args:
            filename: Name of the file to validate
            
        Returns:
            True if extension is allowed, False otherwise
        """
        if '.' not in filename:
            return False
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def ben_graham_preprocessing(image_array: np.ndarray, scale: int = 300) -> np.ndarray:
        """
        Apply Ben Graham preprocessing method for retinal images
        This is a state-of-the-art preprocessing technique that:
        1. Subtracts local average color
        2. Clips values
        3. Scales to desired size
        
        Reference: Winner of Kaggle Diabetic Retinopathy Detection competition
        
        Args:
            image_array: Input image array (H, W, 3)
            scale: Target scale for preprocessing
            
        Returns:
            Preprocessed image array
        """
        # Convert to float
        img = image_array.astype(np.float32)
        
        # Subtract local average color (gaussian blur)
        kernel_size = int(img.shape[0] * 0.1)
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        blurred = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
        img = img - blurred
        
        # Add 128 to center around middle gray
        img = img + 128
        
        # Clip values to valid range
        img = np.clip(img, 0, 255)
        
        return img.astype(np.uint8)
    
    @staticmethod
    def extract_green_channel(image_array: np.ndarray) -> np.ndarray:
        """
        Extract and enhance green channel (most informative for DR detection)
        
        Args:
            image_array: RGB image array
            
        Returns:
            Enhanced green channel as 3-channel image
        """
        # Extract green channel
        green = image_array[:, :, 1]
        
        # Apply CLAHE to green channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        green_enhanced = clahe.apply(green)
        
        # Convert back to 3-channel
        green_3channel = cv2.merge([green_enhanced, green_enhanced, green_enhanced])
        
        return green_3channel
    
    @staticmethod
    def circular_crop(image_array: np.ndarray, pad: int = 10) -> np.ndarray:
        """
        Crop retinal fundus image to circular region of interest
        Removes black borders more effectively
        
        Args:
            image_array: Input image array
            pad: Padding around detected circle
            
        Returns:
            Circularly cropped image
        """
        # Convert to grayscale for circle detection
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array
        
        # Threshold to find bright region
        _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return image_array
        
        # Get largest contour (fundus region)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Fit circle to contour
        (x, y), radius = cv2.minEnclosingCircle(largest_contour)
        center = (int(x), int(y))
        radius = int(radius)
        
        # Create circular mask
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.circle(mask, center, radius - pad, 255, -1)
        
        # Apply mask
        if len(image_array.shape) == 3:
            mask_3channel = cv2.merge([mask, mask, mask])
            result = cv2.bitwise_and(image_array, mask_3channel)
        else:
            result = cv2.bitwise_and(image_array, mask)
        
        # Crop to bounding box
        x_start = max(0, center[0] - radius)
        x_end = min(image_array.shape[1], center[0] + radius)
        y_start = max(0, center[1] - radius)
        y_end = min(image_array.shape[0], center[1] + radius)
        
        cropped = result[y_start:y_end, x_start:x_end]
        
        return cropped
    
    @staticmethod
    def enhance_retinal_image(image: Image.Image) -> Image.Image:
        """
        Enhance retinal fundus image quality
        
        Args:
            image: PIL Image object
            
        Returns:
            Enhanced PIL Image
        """
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.3)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        # Enhance color
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.15)
        
        return image
    
    @staticmethod
    def apply_clahe(image_array: np.ndarray) -> np.ndarray:
        """
        Apply Contrast Limited Adaptive Histogram Equalization (CLAHE)
        Enhanced version with better parameters for retinal images
        
        Args:
            image_array: NumPy array of image in RGB format
            
        Returns:
            Enhanced image array
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
        
        # Split channels
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel with optimized parameters
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels
        lab = cv2.merge([l, a, b])
        
        # Convert back to RGB
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        return enhanced
    
    @staticmethod
    def advanced_augmentation(image_array: np.ndarray, augment_type: str = 'random') -> np.ndarray:
        """
        Apply advanced augmentation techniques
        
        Args:
            image_array: Input image array
            augment_type: Type of augmentation ('random', 'rotate', 'flip', 'brightness')
            
        Returns:
            Augmented image array
        """
        if augment_type == 'random':
            augment_type = np.random.choice(['rotate', 'flip', 'brightness', 'none'])
        
        if augment_type == 'rotate':
            angle = np.random.uniform(-15, 15)
            h, w = image_array.shape[:2]
            M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
            image_array = cv2.warpAffine(image_array, M, (w, h))
        
        elif augment_type == 'flip':
            if np.random.random() > 0.5:
                image_array = cv2.flip(image_array, 1)  # Horizontal flip
            if np.random.random() > 0.5:
                image_array = cv2.flip(image_array, 0)  # Vertical flip
        
        elif augment_type == 'brightness':
            factor = np.random.uniform(0.8, 1.2)
            image_array = np.clip(image_array * factor, 0, 255).astype(np.uint8)
        
        return image_array
    
    @staticmethod
    def preprocess_for_model(image_bytes: bytes, use_ben_graham: bool = True,
                            use_green_channel: bool = False) -> Tuple[np.ndarray, np.ndarray]:
        """
        Enhanced preprocessing pipeline for model inference
        
        Args:
            image_bytes: Raw image bytes from upload
            use_ben_graham: Whether to apply Ben Graham preprocessing
            use_green_channel: Whether to use green channel extraction
            
        Returns:
            Tuple of (preprocessed_array, original_array) for model and visualization
        """
        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Store original for visualization
            original_array = np.array(image)
            
            # Enhance image quality
            image = ImageProcessor.enhance_retinal_image(image)
            
            # Convert to numpy array
            image_array = np.array(image)
            
            # Circular crop to remove black borders
            image_array = ImageProcessor.circular_crop(image_array)
            
            # Apply Ben Graham preprocessing (state-of-the-art)
            if use_ben_graham:
                image_array = ImageProcessor.ben_graham_preprocessing(image_array)
            
            # Extract green channel if requested
            if use_green_channel:
                image_array = ImageProcessor.extract_green_channel(image_array)
            else:
                # Apply CLAHE for better contrast
                image_array = ImageProcessor.apply_clahe(image_array)
            
            # Resize to model input size with high-quality interpolation
            image_resized = cv2.resize(
                image_array, 
                Config.IMAGE_SIZE, 
                interpolation=cv2.INTER_LANCZOS4
            )
            
            # Store resized original for Grad-CAM overlay
            original_resized = cv2.resize(
                original_array,
                Config.IMAGE_SIZE,
                interpolation=cv2.INTER_LANCZOS4
            )
            
            # Normalize pixel values to [0, 1]
            image_normalized = image_resized.astype('float32') / 255.0
            
            # Add batch dimension
            image_batch = np.expand_dims(image_normalized, axis=0)
            
            return image_batch, original_resized
            
        except Exception as e:
            raise ValueError(f"Error preprocessing image: {str(e)}")
    
    @staticmethod
    def _calculate_sharpness(img_array: np.ndarray) -> float:
        """
        Calculate sharpness score using Laplacian variance
        
        Args:
            img_array: Input image array
            
        Returns:
            Sharpness score (higher is sharper)
        """
        # Convert to grayscale if not already
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_array
            
        # Compute the Laplacian variance
        return cv2.Laplacian(gray, cv2.CV_64F).var()
    
    @staticmethod
    def _calculate_brightness(img_array: np.ndarray) -> float:
        """
        Calculate average brightness
        
        Args:
            img_array: Input image array
            
        Returns:
            Average brightness [0, 255]
        """
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        return np.mean(gray)
    
    @staticmethod
    def _calculate_contrast(img_array: np.ndarray) -> float:
        """
        Calculate contrast using standard deviation
        
        Args:
            img_array: Input image array
            
        Returns:
            Contrast score
        """
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        return np.std(gray)
    
    @staticmethod
    def assess_image_quality(image_bytes: bytes) -> Tuple[bool, str, Dict]:
        """
        Enhanced Image Quality Assessment
        Checks sharpness, brightness, and contrast
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Tuple of (is_high_quality, message, quality_metrics)
        """
        SHARPNESS_THRESHOLD = 50.0
        MIN_BRIGHTNESS = 20.0
        MAX_BRIGHTNESS = 235.0
        MIN_CONTRAST = 15.0
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Check if image can be converted to RGB
            if image.mode not in ['RGB', 'RGBA', 'L', 'P']:
                return False, f"Unsupported image mode: {image.mode}", {}
            
            # Convert to numpy array
            img_array = np.array(image.convert('RGB'))
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Calculate quality metrics
            sharpness = ImageProcessor._calculate_sharpness(img_array)
            brightness = ImageProcessor._calculate_brightness(img_array)
            contrast = ImageProcessor._calculate_contrast(img_array)
            
            quality_metrics = {
                "sharpness": float(sharpness),
                "brightness": float(brightness),
                "contrast": float(contrast)
            }
            
            # Check sharpness
            if sharpness < SHARPNESS_THRESHOLD:
                return False, f"Image too blurry (sharpness: {sharpness:.2f}). Please upload a clearer image.", quality_metrics
            
            # Check brightness
            if brightness < MIN_BRIGHTNESS:
                return False, f"Image too dark (brightness: {brightness:.2f}). Please upload a brighter image.", quality_metrics
            
            if brightness > MAX_BRIGHTNESS:
                return False, f"Image too bright (brightness: {brightness:.2f}). Please upload a less overexposed image.", quality_metrics
            
            # Check contrast
            if contrast < MIN_CONTRAST:
                return False, f"Image has insufficient contrast ({contrast:.2f}). Please upload a higher quality image.", quality_metrics
            
            return True, "Image quality is acceptable.", quality_metrics
            
        except Exception as e:
            return False, f"Image quality assessment failed: {str(e)}", {}
    
    @staticmethod
    def validate_image(image_bytes: bytes) -> Tuple[bool, str]:
        """
        Enhanced image validation with quality checks
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Check if image can be converted to RGB
            if image.mode not in ['RGB', 'RGBA', 'L', 'P']:
                return False, f"Unsupported image mode: {image.mode}"
            
            # Check image dimensions
            width, height = image.size
            if width < 100 or height < 100:
                return False, "Image too small (minimum 100x100 pixels)"
            
            if width > 5000 or height > 5000:
                return False, "Image too large (maximum 5000x5000 pixels)"
            
            # Perform quality assessment
            is_high_quality, error_msg, metrics = ImageProcessor.assess_image_quality(image_bytes)
            if not is_high_quality:
                return False, error_msg
            
            return True, ""
            
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
