"""
Access Control Service for RetinaScan AI
Handles authentication, authorization, and RBAC
"""
import logging
import hashlib
import secrets
import jwt
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class Permission(Enum):
    """System permissions"""
    # Patient data access
    READ_PATIENT_DATA = 'read:patient-data'
    WRITE_PATIENT_DATA = 'write:patient-data'
    READ_OWN_DATA = 'read:own-data'
    
    # Analysis and results
    REQUEST_ANALYSIS = 'request:analysis'
    READ_ANALYSIS_RESULTS = 'read:analysis-results'
    READ_OWN_RESULTS = 'read:own-results'
    
    # Anonymous research data
    READ_ANONYMIZED_DATA = 'read:anonymized-data'
    READ_AGGREGATE_STATS = 'read:aggregate-stats'
    
    # Reports and exports
    EXPORT_CLINICAL_REPORTS = 'export:clinical-reports'
    EXPORT_RESEARCH_DATA = 'export:research-data'
    EXPORT_OWN_REPORTS = 'export:own-reports'
    
    # Administrative
    READ_AUDIT_LOGS = 'read:audit-logs'
    MANAGE_USERS = 'manage:users'
    MANAGE_ENCRYPTION_KEYS = 'manage:encryption-keys'
    READ_SYSTEM_METRICS = 'read:system-metrics'
    
    # Model and training
    READ_MODEL_INFO = 'read:model-info'
    TRAIN_MODEL = 'train:model'
    MANAGE_FEDERATED_LEARNING = 'manage:federated-learning'


class Role:
    """Role definition with permissions"""
    
    def __init__(self, name: str, permissions: List[Permission], description: str = ''):
        self.name = name
        self.permissions = set(permissions)
        self.description = description
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if role has specific permission"""
        return permission in self.permissions


class AccessControlService:
    """
    Service for access control, authentication, and authorization
    Implements RBAC with audit logging
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        # JWT secret key for token signing
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        
        # Initialize roles
        self._initialize_roles()
        
        # User sessions (in production, use Redis or database)
        self.active_sessions = {}
        
        # Audit logger reference (will be set externally)
        self.audit_logger = None
    
    def _initialize_roles(self):
        """Initialize system roles with permissions"""
        self.roles = {
            'clinician': Role(
                'clinician',
                [
                    Permission.READ_PATIENT_DATA,
                    Permission.REQUEST_ANALYSIS,
                    Permission.READ_ANALYSIS_RESULTS,
                    Permission.EXPORT_CLINICAL_REPORTS,
                    Permission.READ_MODEL_INFO
                ],
                'Medical professional with access to patient data and analysis'
            ),
            'researcher': Role(
                'researcher',
                [
                    Permission.READ_ANONYMIZED_DATA,
                    Permission.READ_AGGREGATE_STATS,
                    Permission.EXPORT_RESEARCH_DATA,
                    Permission.READ_MODEL_INFO
                ],
                'Researcher with access to anonymized data only'
            ),
            'administrator': Role(
                'administrator',
                [
                    Permission.READ_AUDIT_LOGS,
                    Permission.MANAGE_USERS,
                    Permission.MANAGE_ENCRYPTION_KEYS,
                    Permission.READ_SYSTEM_METRICS,
                    Permission.READ_MODEL_INFO
                ],
                'System administrator with full access'
            ),
            'patient': Role(
                'patient',
                [
                    Permission.READ_OWN_DATA,
                    Permission.REQUEST_ANALYSIS,
                    Permission.READ_OWN_RESULTS,
                    Permission.EXPORT_OWN_REPORTS
                ],
                'Patient with access to own data only'
            ),
            'model_engineer': Role(
                'model_engineer',
                [
                    Permission.READ_ANONYMIZED_DATA,
                    Permission.READ_AGGREGATE_STATS,
                    Permission.TRAIN_MODEL,
                    Permission.MANAGE_FEDERATED_LEARNING,
                    Permission.READ_MODEL_INFO
                ],
                'ML engineer with model training access'
            )
        }
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with username and password
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User object if authenticated, None otherwise
        """
        # In production, verify against database
        # This is a simplified version
        
        # Example verification (replace with actual database lookup)
        if self._verify_password(username, password):
            user = {
                'id': self._generate_user_id(username),
                'username': username,
                'role': self._get_user_role(username),
                'organization': self._get_user_organization(username),
                'authenticated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"User authenticated: {username} ({user['role']})")
            return user
        
        logger.warning(f"Authentication failed for: {username}")
        return None
    
    def create_access_token(self, user: Dict[str, Any], 
                           scope: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create JWT access token for authenticated user
        
        Args:
            user: Authenticated user object
            scope: Optional list of additional scopes
            
        Returns:
            Access token object
        """
        try:
            # Token expiration
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            # Build token payload
            payload = {
                'sub': user['id'],
                'username': user['username'],
                'role': user['role'],
                'org': user.get('organization', 'unknown'),
                'scope': scope or [],
                'iat': datetime.utcnow(),
                'exp': expires_at
            }
            
            # Sign token
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            
            access_token = {
                'token': token,
                'expires_at': expires_at.isoformat(),
                'scope': scope or []
            }
            
            # Store session
            self.active_sessions[user['id']] = {
                'user': user,
                'token': token,
                'created_at': datetime.utcnow()
            }
            
            logger.info(f"Access token created for user: {user['username']}")
            return access_token
            
        except Exception as e:
            logger.error(f"Token creation failed: {str(e)}")
            raise
    
    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT access token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            # Decode and verify token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Check if user session still active
            user_id = payload['sub']
            if user_id not in self.active_sessions:
                logger.warning(f"Token valid but session not found: {user_id}")
                return None
            
            logger.debug(f"Token verified for user: {payload['username']}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
    
    def check_access(self, user: Dict[str, Any], resource: str, 
                    action: str) -> Dict[str, Any]:
        """
        Check if user has permission to perform action on resource
        
        Args:
            user: User object
            resource: Resource identifier
            action: Action to perform
            
        Returns:
            Access decision with granted status and reason
        """
        try:
            role_name = user.get('role', 'patient')
            
            if role_name not in self.roles:
                logger.error(f"Unknown role: {role_name}")
                return {
                    'granted': False,
                    'reason': f'Unknown user role: {role_name}'
                }
            
            role = self.roles[role_name]
            
            # Check permission
            permission = Permission(f"{action}:{resource}")
            has_permission = role.has_permission(permission)
            
            # Log access attempt
            if self.audit_logger:
                self.audit_logger.log_access_attempt(
                    user_id=user['id'],
                    resource=resource,
                    action=action,
                    granted=has_permission
                )
            
            if not has_permission:
                return {
                    'granted': False,
                    'reason': f"User role '{role_name}' lacks permission '{permission.value}'"
                }
            
            # Additional context-based checks
            if resource == 'patient-data' and action == 'read':
                decision = self._check_patient_data_access(user, resource)
                return decision
            
            logger.info(f"Access granted: {user['username']} -> {action}:{resource}")
            return {'granted': True}
            
        except ValueError as e:
            logger.error(f"Invalid permission: {str(e)}")
            return {
                'granted': False,
                'reason': f'Invalid permission format: {action}:{resource}'
            }
        except Exception as e:
            logger.error(f"Access check failed: {str(e)}")
            return {
                'granted': False,
                'reason': f'Access check error: {str(e)}'
            }
    
    def request_emergency_access(self, user: Dict[str, Any], reason: str,
                                supervisor: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request emergency access to normally restricted resources
        
        Args:
            user: User requesting access
            reason: Reason for emergency access
            supervisor: Supervisor authorizing access
            
        Returns:
            Emergency access decision
        """
        try:
            # In production, verify supervisor approval
            approved = self._verify_emergency_access(user, reason, supervisor)
            
            if approved:
                # Create temporary role with elevated permissions
                temporary_role = self._create_temporary_role(user, [
                    Permission.READ_PATIENT_DATA,
                    Permission.WRITE_PATIENT_DATA
                ])
                
                emergency_access = {
                    'granted': True,
                    'temporary_role': temporary_role,
                    'expires_at': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
                    'supervisor': supervisor['id'],
                    'reason': reason
                }
                
                # Log emergency access
                if self.audit_logger:
                    self.audit_logger.log_emergency_access(user, supervisor, reason)
                
                logger.warning(f"Emergency access granted to {user['username']} by {supervisor['username']}")
                return emergency_access
            
            return {'granted': False, 'reason': 'Emergency access not approved'}
            
        except Exception as e:
            logger.error(f"Emergency access request failed: {str(e)}")
            return {'granted': False, 'reason': str(e)}
    
    def revoke_access(self, user_id: str) -> bool:
        """
        Revoke user access by invalidating all sessions
        
        Args:
            user_id: User ID to revoke
            
        Returns:
            True if revocation successful
        """
        try:
            if user_id in self.active_sessions:
                del self.active_sessions[user_id]
                logger.info(f"Access revoked for user: {user_id}")
                return True
            
            logger.warning(f"No active session found for user: {user_id}")
            return False
            
        except Exception as e:
            logger.error(f"Access revocation failed: {str(e)}")
            return False
    
    def _check_patient_data_access(self, user: Dict[str, Any], 
                                  resource: str) -> Dict[str, Any]:
        """Additional checks for patient data access"""
        # Patients can only access their own data
        if user['role'] == 'patient':
            # Check if accessing own data
            # In production, verify patient_id matches user
            pass
        
        # Check organization access
        # In production, verify user is in same organization as patient
        
        return {'granted': True}
    
    def _verify_password(self, username: str, password: str) -> bool:
        """Verify user password (simplified - replace with actual DB lookup)"""
        # In production, use proper password hashing (bcrypt, argon2)
        # and database lookup
        return True  # Simplified
    
    def _get_user_role(self, username: str) -> str:
        """Get user role (simplified - replace with actual DB lookup)"""
        # In production, look up from database
        return 'clinician'  # Simplified
    
    def _get_user_organization(self, username: str) -> str:
        """Get user organization (simplified - replace with actual DB lookup)"""
        return 'default-clinic'  # Simplified
    
    def _generate_user_id(self, username: str) -> str:
        """Generate stable user ID from username"""
        return hashlib.sha256(username.encode('utf-8')).hexdigest()[:16]
    
    def _verify_emergency_access(self, user: Dict[str, Any], reason: str,
                                supervisor: Dict[str, Any]) -> bool:
        """Verify emergency access authorization (simplified)"""
        # In production, implement proper approval workflow
        return True  # Simplified
    
    def _create_temporary_role(self, user: Dict[str, Any],
                              additional_permissions: List[Permission]) -> Dict[str, Any]:
        """Create temporary role with elevated permissions"""
        return {
            'user_id': user['id'],
            'permissions': [p.value for p in additional_permissions],
            'expires_at': (datetime.utcnow() + timedelta(hours=2)).isoformat()
        }

