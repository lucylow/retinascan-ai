import numpy as np
import cv2
from PIL import Image, ImageEnhance
import io
from config import Config

class ImageProcessor:
    """Handles image preprocessing and augmentation for retinal images"""
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def preprocess_image(image_file):
        """
        Preprocess retinal image for model prediction
        Args:
            image_file: FileStorage object from Flask request
        Returns:
            Preprocessed numpy array ready for model prediction
        """
        try:
            # Read image
            image_data = image_file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance image quality
            image = ImageProcessor.enhance_retinal_image(image)
            
            # Convert to numpy array
            image_array = np.array(image)
            
            # Apply retinal image specific preprocessing
            processed_image = ImageProcessor.preprocess_retinal_image(image_array)
            
            # Normalize pixel values
            processed_image = processed_image.astype('float32') / 255.0
            
            # Add batch dimension
            processed_image = np.expand_dims(processed_image, axis=0)
            
            return processed_image
            
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
    
    @staticmethod
    def enhance_retinal_image(image):
        """Enhance retinal image quality"""
        # Increase contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Increase sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        return image
    
    @staticmethod
    def preprocess_retinal_image(image_array):
        """
        Apply retinal image specific preprocessing
        """
        # Resize image
        image_resized = cv2.resize(image_array, Config.IMAGE_SIZE)
        
        # Apply CLAHE for contrast enhancement (common in retinal imaging)
        lab = cv2.cvtColor(image_resized, cv2.COLOR_RGB2LAB)
        lab_planes = list(cv2.split(lab))
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        lab_planes[0] = clahe.apply(lab_planes[0])
        lab = cv2.merge(lab_planes)
        image_enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        # Apply Gaussian blur to reduce noise
        image_enhanced = cv2.GaussianBlur(image_enhanced, (3, 3), 0)
        
        return image_enhanced
    
    @staticmethod
    def validate_image_dimensions(image_array):
        """Validate image meets minimum requirements"""
        height, width = image_array.shape[:2]
        if height < 100 or width < 100:
            raise ValueError("Image dimensions too small. Minimum 100x100 pixels required.")
        return True

