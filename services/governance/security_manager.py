"""
Security and Access Control Manager
Implements authentication, encryption, and role-based access control (RBAC)
for HIPAA and GDPR compliance
"""

import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from typing import Optional, Dict, List, Any
import os


class SecurityManager:
    """
    Implements encryption and access controls required by HIPAA and GDPR
    """
    
    def __init__(self, secret_key: str):
        """
        Initialize SecurityManager with secret key
        
        Args:
            secret_key: Secret key for JWT token signing (should be from env var)
        """
        self.secret_key = secret_key
        self.algorithm = 'HS256'
        # Token expiration: 8 hours for security (HIPAA recommends short-lived tokens)
        self.token_expiration_hours = int(os.getenv('TOKEN_EXPIRATION_HOURS', '8'))
    
    def hash_password(self, password: str) -> bytes:
        """
        Hash passwords using bcrypt - required for PHI access
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password as bytes
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def check_password(self, password: str, hashed: bytes) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            hashed: Hashed password bytes
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            if isinstance(hashed, str):
                hashed = hashed.encode('utf-8')
            return bcrypt.checkpw(password.encode('utf-8'), hashed)
        except Exception:
            return False
    
    def generate_token(self, user_id: str, role: str, permissions: List[str]) -> str:
        """
        Generate JWT token with role-based permissions
        
        Args:
            user_id: Unique user identifier
            role: User role (clinician, researcher, patient, admin)
            permissions: List of permissions for the user
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'role': role,
            'permissions': permissions,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiration_hours)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return payload
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh an existing token if it's still valid
        
        Args:
            token: Existing JWT token
            
        Returns:
            New token string if refresh successful, None otherwise
        """
        payload = self.verify_token(token)
        if payload:
            # Remove exp and iat from payload for refresh
            payload.pop('exp', None)
            payload.pop('iat', None)
            return self.generate_token(
                payload['user_id'],
                payload['role'],
                payload.get('permissions', [])
            )
        return None


class RBAC:
    """
    Role-Based Access Control for PHI and personal data
    Implements principle of least privilege for HIPAA compliance
    """
    
    def __init__(self):
        """Initialize RBAC with predefined roles and permissions"""
        self.roles = {
            'clinician': [
                'view_patient_data',
                'submit_diagnosis',
                'view_ai_results',
                'modify_patient_records',
                'access_phi'
            ],
            'researcher': [
                'view_anonymized_data',
                'analyze_trends',
                'export_aggregated_data',
                'access_anonymized_datasets'
            ],
            'patient': [
                'view_own_data',
                'consent_management',
                'request_data_portability',
                'request_data_erasure'
            ],
            'admin': [
                'manage_users',
                'audit_logs',
                'data_retention',
                'system_configuration',
                'incident_management',
                'access_all_data'
            ],
            'readonly': [
                'view_patient_data',
                'view_ai_results'
            ]
        }
        
        # Data access matrix: maps role and data type to access level
        self.access_matrix = {
            'clinician': {
                'phi': 'full',
                'anonymous': 'full',
                'sensitive': 'restricted',
                'genetic': 'none'  # Requires special authorization
            },
            'researcher': {
                'phi': 'none',
                'anonymous': 'full',
                'sensitive': 'none',
                'genetic': 'none'
            },
            'patient': {
                'phi': 'own',
                'anonymous': 'full',
                'sensitive': 'own',
                'genetic': 'own'
            },
            'admin': {
                'phi': 'full',
                'anonymous': 'full',
                'sensitive': 'full',
                'genetic': 'full'
            },
            'readonly': {
                'phi': 'read_only',
                'anonymous': 'read_only',
                'sensitive': 'none',
                'genetic': 'none'
            }
        }
    
    def has_permission(self, role: str, permission: str) -> bool:
        """
        Check if role has specific permission
        
        Args:
            role: User role
            permission: Permission to check
            
        Returns:
            True if role has permission, False otherwise
        """
        return permission in self.roles.get(role, [])
    
    def get_data_access_level(self, role: str, data_type: str) -> str:
        """
        Determine data access level based on role and data type
        
        Args:
            role: User role
            data_type: Type of data (phi, anonymous, sensitive, genetic)
            
        Returns:
            Access level: 'full', 'read_only', 'restricted', 'own', or 'none'
        """
        return self.access_matrix.get(role, {}).get(data_type, 'none')
    
    def can_access_patient_data(self, role: str, patient_id: str, user_id: str) -> bool:
        """
        Check if user can access specific patient data
        
        Args:
            role: User role
            patient_id: Target patient ID
            user_id: Requesting user ID
            
        Returns:
            True if access allowed, False otherwise
        """
        access_level = self.get_data_access_level(role, 'phi')
        
        if access_level == 'full':
            return True
        elif access_level == 'own':
            return patient_id == user_id
        elif access_level == 'read_only':
            return self.has_permission(role, 'view_patient_data')
        else:
            return False
    
    def get_allowed_permissions(self, role: str) -> List[str]:
        """
        Get all permissions for a role
        
        Args:
            role: User role
            
        Returns:
            List of permission strings
        """
        return self.roles.get(role, [])


# Flask decorators for route protection

def token_required(f):
    """
    Decorator for protecting routes requiring authentication
    Extracts and validates JWT token from Authorization header
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token is missing. Authentication required.'
            }), 401
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Get secret key from app config
        secret_key = current_app.config.get('SECRET_KEY')
        if not secret_key:
            return jsonify({
                'success': False,
                'error': 'Server configuration error'
            }), 500
        
        security_mgr = SecurityManager(secret_key)
        payload = security_mgr.verify_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
        
        # Attach user info to request context
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated


def permission_required(permission: str):
    """
    Decorator for role-based permission checking
    Must be used after @token_required
    
    Args:
        permission: Required permission string
    """
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            rbac = RBAC()
            user_role = request.user.get('role')
            
            if not user_role:
                return jsonify({
                    'success': False,
                    'error': 'User role not found'
                }), 403
            
            if not rbac.has_permission(user_role, permission):
                return jsonify({
                    'success': False,
                    'error': f'Insufficient permissions. Required: {permission}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def data_access_required(data_type: str = 'phi', access_level: str = 'read'):
    """
    Decorator for data access level checking
    Validates user can access specific data type at required level
    
    Args:
        data_type: Type of data (phi, anonymous, sensitive, genetic)
        access_level: Required access level (read, write, full)
    """
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            rbac = RBAC()
            user_role = request.user.get('role')
            
            if not user_role:
                return jsonify({
                    'success': False,
                    'error': 'User role not found'
                }), 403
            
            user_access = rbac.get_data_access_level(user_role, data_type)
            
            # Check access level hierarchy
            access_hierarchy = ['none', 'read_only', 'restricted', 'own', 'full']
            required_index = access_hierarchy.index(access_level) if access_level in access_hierarchy else 0
            user_index = access_hierarchy.index(user_access) if user_access in access_hierarchy else -1
            
            if user_index < required_index:
                return jsonify({
                    'success': False,
                    'error': f'Insufficient data access. Required: {access_level}, Current: {user_access}'
                }), 403
            
            # For 'own' access level, verify patient_id matches user_id
            if user_access == 'own' and 'patient_id' in kwargs:
                if kwargs['patient_id'] != request.user.get('user_id'):
                    return jsonify({
                        'success': False,
                        'error': 'Access denied: Can only access own data'
                    }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator
