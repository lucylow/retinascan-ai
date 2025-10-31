"""
Security Middleware for RetinaScan AI
Middleware for authentication, authorization, and security headers
"""
import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """
    Middleware for request security
    Handles input sanitization, authentication, and security headers
    """
    
    def __init__(self, access_control=None, audit_logger=None):
        self.access_control = access_control
        self.audit_logger = audit_logger
    
    async def handle_request(self, request: Any, endpoint: str, 
                           resource: str, action: str) -> Dict[str, Any]:
        """
        Process incoming request through security middleware
        
        Args:
            request: Request object
            endpoint: API endpoint
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            Validation result with user info if authenticated
        """
        try:
            # 1. Validate and sanitize input
            sanitized_request = await self._sanitize_input(request)
            
            # 2. Authenticate user
            user = await self._authenticate_user(sanitized_request)
            if not user:
                return {
                    'valid': False,
                    'error': 'Authentication failed'
                }
            
            # 3. Check authorization
            if self.access_control:
                access_decision = self.access_control.check_access(
                    user, resource, action
                )
                
                if not access_decision['granted']:
                    if self.audit_logger:
                        self.audit_logger.log_security_event({
                            'category': 'UNAUTHORIZED_ACCESS',
                            'severity': 'WARNING',
                            'userId': user.get('id'),
                            'description': access_decision['reason']
                        })
                    return {
                        'valid': False,
                        'error': access_decision['reason']
                    }
            
            # 4. Log successful access
            if self.audit_logger:
                self.audit_logger.log_access_attempt(
                    user_id=user['id'],
                    resource=resource,
                    action=action,
                    granted=True
                )
            
            return {
                'valid': True,
                'user': user,
                'sanitized_request': sanitized_request
            }
            
        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            return {
                'valid': False,
                'error': 'Security processing failed'
            }
    
    def add_security_headers(self, response: Any) -> Any:
        """
        Add security headers to response
        
        Args:
            response: Response object
            
        Returns:
            Response with security headers
        """
        security_headers = {
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
        
        for header, value in security_headers.items():
            if hasattr(response, 'headers'):
                response.headers[header] = value
        
        return response
    
    async def _sanitize_input(self, request: Any) -> Dict[str, Any]:
        """Sanitize input data"""
        sanitized = {}
        
        try:
            # Get request data based on framework
            request_data = {}
            if hasattr(request, 'json'):
                request_data = request.json
            elif hasattr(request, 'form'):
                request_data = request.form
            elif hasattr(request, 'data'):
                request_data = request.data
            
            # Sanitize string values
            for key, value in request_data.items():
                if isinstance(value, str):
                    sanitized[key] = self._sanitize_string(value)
                else:
                    sanitized[key] = value
            
            # Validate input types
            await self._validate_input_types(sanitized)
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Input sanitization failed: {str(e)}")
            return {}
    
    def _sanitize_string(self, input_str: str) -> str:
        """
        Sanitize string input to prevent injection attacks
        
        Args:
            input_str: Input string
            
        Returns:
            Sanitized string
        """
        if not isinstance(input_str, str):
            return str(input_str)
        
        # Remove potentially dangerous characters and patterns
        sanitized = input_str
        
        # Remove script tags and content
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove event handlers
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
        
        # Remove javascript: protocol
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        
        # Remove potentially dangerous characters
        sanitized = sanitized.replace('<', '').replace('>', '')
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    async def _validate_input_types(self, data: Dict[str, Any]) -> None:
        """Validate input data types"""
        # Implement type validation
        pass
    
    async def _authenticate_user(self, request: Any) -> Optional[Dict[str, Any]]:
        """Authenticate user from request"""
        try:
            # Extract token from headers
            token = self._extract_token(request)
            
            if not token:
                return None
            
            # Verify token
            if self.access_control:
                user_payload = self.access_control.verify_access_token(token)
                if user_payload:
                    return {
                        'id': user_payload['sub'],
                        'username': user_payload['username'],
                        'role': user_payload['role'],
                        'organization': user_payload.get('org', 'unknown')
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return None
    
    def _extract_token(self, request: Any) -> Optional[str]:
        """Extract authentication token from request"""
        try:
            if hasattr(request, 'headers'):
                auth_header = request.headers.get('Authorization', '')
                if auth_header.startswith('Bearer '):
                    return auth_header[7:]
            return None
        except:
            return None

