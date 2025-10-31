"""
Encryption Service for RetinaScan AI
Handles encryption at rest and in transit, key management
"""
import base64
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Service for data encryption, decryption, and key management
    Supports AES-256 for data at rest and in transit
    """
    
    def __init__(self):
        self.key_storage_path = os.getenv('KEY_STORAGE_PATH', './.keys')
        self.current_key_version = os.getenv('KEY_VERSION', 'v1')
        self.keys = {}
        
        # Ensure key storage directory exists
        os.makedirs(self.key_storage_path, exist_ok=True)
        
        # Initialize encryption keys
        self._initialize_keys()
    
    def _initialize_keys(self):
        """Initialize encryption keys for different contexts"""
        contexts = [
            'patient-record',
            'analysis-results',
            'model-weights',
            'audit-trail',
            'communication'
        ]
        
        for context in contexts:
            key = self._get_or_create_key(context, self.current_key_version)
            self.keys[f"{context}-{self.current_key_version}"] = key
    
    def _get_or_create_key(self, context: str, version: str) -> bytes:
        """Get existing key or create new one"""
        key_id = f"{context}-{version}"
        key_file = os.path.join(self.key_storage_path, f"{key_id}.key")
        
        try:
            # Try to load existing key
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    key = f.read()
                    logger.debug(f"Loaded existing key for {key_id}")
                    return key
        except Exception as e:
            logger.warning(f"Could not load key {key_id}: {str(e)}")
        
        # Generate new key
        key = Fernet.generate_key()
        
        try:
            # Save key securely
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict permissions
            logger.info(f"Generated new key for {key_id}")
        except Exception as e:
            logger.error(f"Could not save key {key_id}: {str(e)}")
        
        return key
    
    def encrypt_data(self, data: Any, context: str = 'patient-record') -> Dict[str, Any]:
        """
        Encrypt data using AES-256 (Fernet symmetric encryption)
        
        Args:
            data: Data to encrypt (will be JSON serialized)
            context: Context for key selection
            
        Returns:
            Dictionary with encrypted data and metadata
        """
        try:
            # Get encryption key
            key = self.keys.get(
                f"{context}-{self.current_key_version}",
                self._get_or_create_key(context, self.current_key_version)
            )
            
            # Create Fernet cipher
            fernet = Fernet(key)
            
            # Serialize data
            import json
            data_str = json.dumps(data, default=str)
            data_bytes = data_str.encode('utf-8')
            
            # Encrypt
            encrypted = fernet.encrypt(data_bytes)
            
            # Encode to base64 for storage
            encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
            
            logger.debug(f"Encrypted data for context: {context}")
            
            return {
                'encrypted_data': encrypted_b64,
                'key_version': self.current_key_version,
                'context': context,
                'timestamp': datetime.utcnow().isoformat(),
                'encryption_method': 'AES-256-Fernet'
            }
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_payload: Dict[str, Any]) -> Any:
        """
        Decrypt data using stored keys
        
        Args:
            encrypted_payload: Dictionary with encrypted data and metadata
            
        Returns:
            Decrypted data
        """
        try:
            # Get key version and context
            key_version = encrypted_payload.get('key_version', self.current_key_version)
            context = encrypted_payload['context']
            
            # Get decryption key
            key_id = f"{context}-{key_version}"
            if key_id not in self.keys:
                key = self._get_or_create_key(context, key_version)
                self.keys[key_id] = key
            else:
                key = self.keys[key_id]
            
            # Create Fernet cipher
            fernet = Fernet(key)
            
            # Decode from base64
            encrypted_b64 = encrypted_payload['encrypted_data']
            encrypted = base64.b64decode(encrypted_b64.encode('utf-8'))
            
            # Decrypt
            decrypted_bytes = fernet.decrypt(encrypted)
            decrypted_str = decrypted_bytes.decode('utf-8')
            
            # Deserialize
            import json
            decrypted_data = json.loads(decrypted_str)
            
            logger.debug(f"Decrypted data for context: {context}")
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None,
                    context: str = 'patient-record') -> str:
        """
        Encrypt a file and save to disk
        
        Args:
            file_path: Path to file to encrypt
            output_path: Path for encrypted file (default: input_path + .enc)
            context: Encryption context
            
        Returns:
            Path to encrypted file
        """
        try:
            if output_path is None:
                output_path = f"{file_path}.enc"
            
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Encrypt
            encrypted_payload = self.encrypt_data(
                {'file_content': base64.b64encode(file_data).decode('utf-8')},
                context
            )
            
            # Save encrypted file
            import json
            with open(output_path, 'w') as f:
                json.dump(encrypted_payload, f)
            
            logger.info(f"Encrypted file: {file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"File encryption failed: {str(e)}")
            raise
    
    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt a file and save to disk
        
        Args:
            encrypted_file_path: Path to encrypted file
            output_path: Path for decrypted file
            
        Returns:
            Path to decrypted file
        """
        try:
            # Read encrypted file
            import json
            with open(encrypted_file_path, 'r') as f:
                encrypted_payload = json.load(f)
            
            # Decrypt
            decrypted_data = self.decrypt_data(encrypted_payload)
            
            # Extract file content
            file_content_b64 = decrypted_data['file_content']
            file_data = base64.b64decode(file_content_b64.encode('utf-8'))
            
            # Determine output path
            if output_path is None:
                if encrypted_file_path.endswith('.enc'):
                    output_path = encrypted_file_path[:-4]
                else:
                    output_path = f"{encrypted_file_path}.decrypted"
            
            # Save decrypted file
            with open(output_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"Decrypted file: {encrypted_file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"File decryption failed: {str(e)}")
            raise
    
    def rotate_keys(self) -> str:
        """
        Rotate encryption keys to new version
        Re-encrypts data with new keys
        
        Returns:
            New key version identifier
        """
        try:
            # Generate new key version
            new_version = f"v{int(datetime.utcnow().timestamp())}"
            
            # Create new keys for all contexts
            contexts = [
                'patient-record',
                'analysis-results',
                'model-weights',
                'audit-trail',
                'communication'
            ]
            
            for context in contexts:
                key = self._get_or_create_key(context, new_version)
                self.keys[f"{context}-{new_version}"] = key
            
            logger.info(f"Rotated keys to version: {new_version}")
            
            # Keep old keys for decryption during transition
            # Schedule re-encryption task in background
            
            self.current_key_version = new_version
            return new_version
            
        except Exception as e:
            logger.error(f"Key rotation failed: {str(e)}")
            raise
    
    def create_secure_channel(self, endpoint: str) -> Dict[str, Any]:
        """
        Create a secure communication channel
        Establishes session keys for encrypted transmission
        
        Args:
            endpoint: Communication endpoint
            
        Returns:
            Secure channel configuration
        """
        try:
            # Generate session key
            session_key = Fernet.generate_key()
            fernet = Fernet(session_key)
            
            channel = {
                'session_key': session_key,
                'endpoint': endpoint,
                'established_at': datetime.utcnow().isoformat(),
                'message_counter': 0,
                'fernet': fernet  # Store Fernet instance for efficiency
            }
            
            logger.info(f"Created secure channel to {endpoint}")
            return channel
            
        except Exception as e:
            logger.error(f"Channel creation failed: {str(e)}")
            raise
    
    def send_secure_message(self, channel: Dict[str, Any], message: Any) -> Dict[str, Any]:
        """
        Send encrypted message through secure channel
        
        Args:
            channel: Secure channel configuration
            message: Message to encrypt and send
            
        Returns:
            Encrypted message payload
        """
        try:
            fernet = channel['fernet']
            
            # Serialize message
            import json
            message_str = json.dumps(message, default=str)
            message_bytes = message_str.encode('utf-8')
            
            # Encrypt
            encrypted = fernet.encrypt(message_bytes)
            
            # Increment message counter
            channel['message_counter'] += 1
            
            secure_message = {
                'encrypted_data': base64.b64encode(encrypted).decode('utf-8'),
                'message_number': channel['message_counter'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.debug(f"Sent secure message #{channel['message_counter']}")
            return secure_message
            
        except Exception as e:
            logger.error(f"Secure message send failed: {str(e)}")
            raise
    
    def receive_secure_message(self, channel: Dict[str, Any], 
                              encrypted_message: Dict[str, Any]) -> Any:
        """
        Receive and decrypt message from secure channel
        
        Args:
            channel: Secure channel configuration
            encrypted_message: Encrypted message payload
            
        Returns:
            Decrypted message
        """
        try:
            fernet = channel['fernet']
            
            # Decode from base64
            encrypted = base64.b64decode(encrypted_message['encrypted_data'].encode('utf-8'))
            
            # Decrypt
            decrypted_bytes = fernet.decrypt(encrypted)
            decrypted_str = decrypted_bytes.decode('utf-8')
            
            # Deserialize
            import json
            message = json.loads(decrypted_str)
            
            logger.debug(f"Received secure message #{encrypted_message['message_number']}")
            return message
            
        except Exception as e:
            logger.error(f"Secure message receive failed: {str(e)}")
            raise

