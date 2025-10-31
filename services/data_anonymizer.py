"""
Data Anonymization Service for RetinaScan AI
Handles anonymization and de-identification of patient data
"""
import hashlib
import hmac
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import os
import numpy as np
from PIL import Image
import cv2

logger = logging.getLogger(__name__)


class DataAnonymizer:
    """
    Service for anonymizing patient data with configurable profiles
    Supports DICOM metadata, pixel-level anonymization, and PHI removal
    """
    
    def __init__(self):
        self.anonymization_profiles = {
            'research': {
                'remove_fields': ['name', 'address', 'phone', 'email', 'ssn', 'mrn', 'zip'],
                'hash_fields': ['patientId'],
                'keep_fields': ['age', 'gender', 'diagnosis', 'diabetesType'],
                'date_shift': True,
                'generalization': {
                    'age': '5-year-buckets',
                    'dates': 'year-only'
                }
            },
            'public': {
                'remove_fields': ['name', 'address', 'phone', 'email', 'ssn', 'mrn', 
                                 'patientId', 'zip', 'city'],
                'keep_fields': ['ageRange', 'gender', 'diagnosis'],
                'date_shift': True,
                'generalization': {
                    'age': '10-year-buckets',
                    'dates': 'year-only',
                    'location': 'state-level'
                }
            },
            'limited': {
                'remove_fields': ['name', 'address', 'phone', 'ssn'],
                'hash_fields': ['patientId', 'mrn'],
                'keep_fields': ['age', 'gender', 'exactDates', 'zipCode'],
                'date_shift': False
            },
            'clinical': {
                'remove_fields': ['ssn', 'insuranceNumber'],
                'hash_fields': [],  # Keep identifiers for clinical use
                'keep_fields': ['name', 'address', 'phone', 'email', 'mrn', 
                               'patientId', 'age', 'gender', 'diagnosis', 'dates'],
                'date_shift': False
            }
        }
        
        # Secret key for hashing (should be stored securely in production)
        self.secret_key = os.getenv('ANONYMIZATION_SECRET', 
                                   'default-secret-change-in-production').encode('utf-8')
    
    def anonymize_patient_data(self, patient_data: Dict[str, Any], 
                               profile: str = 'research') -> Dict[str, Any]:
        """
        Anonymize patient data according to specified profile
        
        Args:
            patient_data: Dictionary containing patient information
            profile: Anonymization profile to use ('research', 'public', 'limited', 'clinical')
            
        Returns:
            Anonymized patient data dictionary
        """
        if profile not in self.anonymization_profiles:
            logger.warning(f"Unknown profile '{profile}', using 'research'")
            profile = 'research'
        
        config = self.anonymization_profiles[profile]
        anonymized = {}
        
        try:
            # Process each field
            for key, value in patient_data.items():
                if key in config['remove_fields']:
                    continue  # Skip removed fields
                
                if key in config.get('hash_fields', []):
                    anonymized[key] = self._hash_value(str(value))
                
                elif key in config.get('generalization', {}):
                    rule = config['generalization'][key]
                    anonymized[key] = self._generalize_value(value, rule)
                
                elif key in config['keep_fields']:
                    anonymized[key] = value
                else:
                    # Default: remove field if not explicitly handled
                    continue
            
            # Apply date shifting if configured
            if config.get('date_shift', False) and 'dates' in patient_data:
                patient_id = patient_data.get('patientId', 
                                             patient_data.get('mrn', 'default'))
                anonymized['dates'] = self._shift_dates(
                    patient_data['dates'], 
                    patient_id
                )
            
            # Add anonymization metadata
            anonymized['_anonymization'] = {
                'profile': profile,
                'timestamp': datetime.utcnow().isoformat(),
                'original_data_hash': self._calculate_data_hash(patient_data)
            }
            
            logger.info(f"Successfully anonymized patient data with profile: {profile}")
            return anonymized
            
        except Exception as e:
            logger.error(f"Error during anonymization: {str(e)}")
            raise
    
    def anonymize_dicom_metadata(self, dicom_tags: Dict[str, Any], 
                                 profile: str = 'research') -> Dict[str, Any]:
        """
        Anonymize DICOM metadata according to standard guidelines
        
        Args:
            dicom_tags: Dictionary of DICOM tags
            profile: Anonymization profile
            
        Returns:
            Anonymized DICOM tags
        """
        config = self.anonymization_profiles[profile]
        anonymized_tags = {}
        
        # DICOM standard fields to remove
        standard_remove = [
            'PatientName', 'PatientID', 'PatientBirthDate', 'PatientSex',
            'PatientAddress', 'PatientTelephoneNumbers', 'PatientAge',
            'StudyDate', 'StudyTime', 'AccessionNumber', 'ReferringPhysicianName',
            'InstitutionName', 'InstitutionAddress'
        ]
        
        # Keep only non-PHI fields
        safe_fields = ['StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID',
                      'Modality', 'Manufacturer', 'ImageType']
        
        for tag in safe_fields:
            if tag in dicom_tags:
                anonymized_tags[tag] = dicom_tags[tag]
        
        # Add anonymization metadata
        anonymized_tags['_anonymization'] = {
            'profile': profile,
            'timestamp': datetime.utcnow().isoformat(),
            'fields_removed': len(standard_remove)
        }
        
        return anonymized_tags
    
    def anonymize_retina_image(self, image_array: np.ndarray, 
                              detect_text: bool = False) -> np.ndarray:
        """
        Remove PHI from retinal images (burned-in text overlays)
        
        Args:
            image_array: NumPy array of the retinal image
            detect_text: Whether to detect and remove text regions
            
        Returns:
            Anonymized image array
        """
        try:
            anonymized_image = image_array.copy()
            
            if detect_text:
                # Find and mask text regions in common overlay positions
                text_regions = self._detect_text_regions(image_array)
                
                for region in text_regions:
                    # Black out text regions
                    anonymized_image[
                        region['y']:region['y']+region['height'],
                        region['x']:region['x']+region['width']
                    ] = 0
            
            logger.debug("Image anonymization completed")
            return anonymized_image
            
        except Exception as e:
            logger.error(f"Error during image anonymization: {str(e)}")
            raise
    
    def _hash_value(self, value: str) -> str:
        """Hash a value using HMAC-SHA256"""
        try:
            hash_obj = hmac.new(
                self.secret_key,
                value.encode('utf-8'),
                hashlib.sha256
            )
            return hash_obj.hexdigest()[:32]  # Truncate to 32 chars
        except Exception as e:
            logger.error(f"Error hashing value: {str(e)}")
            return ''
    
    def _generalize_value(self, value: Any, rule: str) -> Any:
        """Generalize a value according to a rule"""
        try:
            if rule == '5-year-buckets':
                age = int(value)
                bucket_start = (age // 5) * 5
                return f"{bucket_start}-{bucket_start + 4}"
            
            elif rule == '10-year-buckets':
                age = int(value)
                bucket_start = (age // 10) * 10
                return f"{bucket_start}-{bucket_start + 9}"
            
            elif rule == 'year-only':
                date_obj = datetime.fromisoformat(str(value))
                return str(date_obj.year)
            
            elif rule == 'state-level':
                # Extract state from address
                if isinstance(value, str):
                    parts = value.split(',')
                    if len(parts) >= 2:
                        return parts[-1].strip()
                return 'Unknown'
            
            return value
            
        except Exception as e:
            logger.warning(f"Generalization failed: {str(e)}")
            return value
    
    def _shift_dates(self, dates: Dict[str, str], patient_id: str) -> Dict[str, str]:
        """Apply deterministic date shifting"""
        try:
            # Calculate deterministic shift based on patient ID
            shift_days = self._calculate_date_shift(patient_id)
            
            shifted_dates = {}
            for key, date_str in dates.items():
                try:
                    date_obj = datetime.fromisoformat(str(date_str))
                    shifted_date = date_obj + timedelta(days=shift_days)
                    shifted_dates[key] = shifted_date.isoformat()
                except:
                    shifted_dates[key] = date_str
            
            return shifted_dates
            
        except Exception as e:
            logger.error(f"Date shifting failed: {str(e)}")
            return dates
    
    def _calculate_date_shift(self, patient_id: str) -> int:
        """Calculate deterministic date shift"""
        hash_val = self._hash_value(patient_id)
        hash_int = int(hash_val[:8], 16)
        # Shift between -365 and +365 days
        return (hash_int % 730) - 365
    
    def _calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash of original data for audit trail"""
        try:
            data_str = str(sorted(data.items()))
            return hashlib.sha256(data_str.encode('utf-8')).hexdigest()[:16]
        except:
            return ''
    
    def _detect_text_regions(self, image: np.ndarray) -> List[Dict[str, int]]:
        """
        Detect common text overlay positions in medical images
        Returns regions where text might be burned in
        """
        regions = []
        
        if len(image.shape) != 2:
            # Convert to grayscale if color
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        height, width = gray.shape
        
        # Common text overlay positions (corners and edges)
        potential_regions = [
            {'x': 0, 'y': 0, 'width': int(width * 0.2), 'height': int(height * 0.1)},  # Top-left
            {'x': int(width * 0.8), 'y': 0, 'width': int(width * 0.2), 'height': int(height * 0.1)},  # Top-right
            {'x': 0, 'y': int(height * 0.9), 'width': int(width * 0.2), 'height': int(height * 0.1)},  # Bottom-left
            {'x': int(width * 0.8), 'y': int(height * 0.9), 'width': int(width * 0.2), 'height': int(height * 0.1)},  # Bottom-right
            {'x': 0, 'y': int(height * 0.45), 'width': int(width * 0.15), 'height': int(height * 0.1)},  # Left-middle
            {'x': int(width * 0.85), 'y': int(height * 0.45), 'width': int(width * 0.15), 'height': int(height * 0.1)}  # Right-middle
        ]
        
        # Optional: Use OpenCV edge detection to find actual text regions
        # This is a simplified version - production should use proper OCR
        
        return potential_regions
    
    def validate_anonymization(self, anonymized_data: Dict[str, Any]) -> bool:
        """
        Validate that anonymization was successful
        Checks for presence of PHI indicators
        """
        phi_indicators = ['@', '.com', 'http', 'patient name', 'social security']
        
        data_str = str(anonymized_data).lower()
        
        for indicator in phi_indicators:
            if indicator in data_str:
                logger.warning(f"Potential PHI detected: {indicator}")
                return False
        
        return True

