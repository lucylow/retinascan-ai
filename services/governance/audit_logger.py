"""
Comprehensive Audit Logging System
Implements detailed audit trails for HIPAA and GDPR compliance
"""

import sqlite3
import json
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from flask import request
import os
from pathlib import Path


class AuditLogger:
    """
    Comprehensive audit logging for GDPR and HIPAA compliance
    Maintains detailed logs of all system activities, data access, and user actions
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize AuditLogger with database path
        
        Args:
            db_path: Path to SQLite database file (default: governance_audit.db)
        """
        if db_path is None:
            # Default to data directory in backend
            db_dir = Path(__file__).parent.parent.parent / 'backend' / 'data'
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / 'governance_audit.db')
        
        self.db_path = db_path
        self._create_tables()
    
    @contextmanager
    def _get_connection(self):
        """
        Context manager for database connections
        Ensures proper transaction handling and cleanup
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _create_tables(self):
        """Create audit log and data access tables"""
        with self._get_connection() as conn:
            # General audit logs table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    session_id TEXT,
                    severity TEXT DEFAULT 'info'
                )
            ''')
            
            # Data access logs table - HIPAA requirement
            conn.execute('''
                CREATE TABLE IF NOT EXISTS data_access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    patient_id TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    access_type TEXT NOT NULL,
                    purpose TEXT,
                    justification TEXT,
                    ip_address TEXT,
                    success BOOLEAN DEFAULT 1
                )
            ''')
            
            # Consent records table - GDPR requirement
            conn.execute('''
                CREATE TABLE IF NOT EXISTS consent_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT NOT NULL,
                    consent_type TEXT NOT NULL,
                    granted BOOLEAN NOT NULL,
                    timestamp TEXT NOT NULL,
                    expiration TEXT,
                    purpose TEXT,
                    version TEXT NOT NULL,
                    ip_address TEXT,
                    method TEXT,
                    revocable BOOLEAN DEFAULT 1
                )
            ''')
            
            # Model usage audit - for AI governance
            conn.execute('''
                CREATE TABLE IF NOT EXISTS model_usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    patient_id TEXT,
                    model_version TEXT NOT NULL,
                    input_hash TEXT,
                    prediction_result TEXT,
                    confidence_score REAL,
                    processing_time_ms INTEGER,
                    decision_path TEXT
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_data_access_patient ON data_access_logs(patient_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_data_access_timestamp ON data_access_logs(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_consent_patient ON consent_records(patient_id)')
    
    def log_data_access(
        self,
        user_id: str,
        patient_id: str,
        data_type: str,
        access_type: str,
        purpose: str,
        justification: Optional[str] = None,
        success: bool = True
    ):
        """
        Log all data access for HIPAA compliance
        
        Args:
            user_id: ID of user accessing data
            patient_id: ID of patient whose data is accessed
            data_type: Type of data (phi, anonymous, sensitive, etc.)
            access_type: Type of access (read, write, delete, export)
            purpose: Purpose of access (treatment, payment, healthcare_operations, etc.)
            justification: Optional justification for access
            success: Whether access was successful
        """
        ip_address = request.remote_addr if request else 'system'
        
        with self._get_connection() as conn:
            conn.execute('''
                INSERT INTO data_access_logs 
                (timestamp, user_id, patient_id, data_type, access_type, purpose, justification, ip_address, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.utcnow().isoformat(),
                user_id,
                patient_id,
                data_type,
                access_type,
                purpose,
                justification,
                ip_address,
                1 if success else 0
            ))
    
    def log_audit_event(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = 'info'
    ):
        """
        Log general audit events
        
        Args:
            user_id: ID of user performing action
            action: Action performed (create, read, update, delete, login, logout, etc.)
            resource_type: Type of resource (patient, diagnosis, model, user, etc.)
            resource_id: Optional ID of specific resource
            details: Optional additional details as dictionary
            severity: Severity level (info, warning, error, critical)
        """
        ip_address = request.remote_addr if request else 'system'
        user_agent = request.headers.get('User-Agent') if request else 'system'
        session_id = request.headers.get('X-Session-ID') if request else None
        
        with self._get_connection() as conn:
            conn.execute('''
                INSERT INTO audit_logs 
                (timestamp, user_id, action, resource_type, resource_id, details, ip_address, user_agent, session_id, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.utcnow().isoformat(),
                user_id,
                action,
                resource_type,
                resource_id,
                json.dumps(details) if details else None,
                ip_address,
                user_agent,
                session_id,
                severity
            ))
    
    def record_consent(
        self,
        patient_id: str,
        consent_type: str,
        granted: bool,
        expiration: Optional[str] = None,
        purpose: str = "",
        version: str = "1.0",
        method: str = "web_form"
    ):
        """
        Record patient consent for GDPR compliance
        
        Args:
            patient_id: ID of patient granting/revoking consent
            consent_type: Type of consent (data_processing, research, marketing, etc.)
            granted: True if consent granted, False if revoked
            expiration: Optional expiration date (ISO format)
            purpose: Purpose of consent
            version: Version of consent form
            method: Method used (web_form, paper, verbal, etc.)
        """
        ip_address = request.remote_addr if request else 'system'
        
        with self._get_connection() as conn:
            conn.execute('''
                INSERT INTO consent_records 
                (patient_id, consent_type, granted, timestamp, expiration, purpose, version, ip_address, method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_id,
                consent_type,
                1 if granted else 0,
                datetime.utcnow().isoformat(),
                expiration,
                purpose,
                version,
                ip_address,
                method
            ))
    
    def get_consent_status(self, patient_id: str, consent_type: str) -> Optional[Dict[str, Any]]:
        """
        Check current consent status for a patient
        
        Args:
            patient_id: Patient ID
            consent_type: Type of consent to check
            
        Returns:
            Most recent consent record as dict, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM consent_records 
                WHERE patient_id = ? AND consent_type = ? 
                ORDER BY timestamp DESC LIMIT 1
            ''', (patient_id, consent_type))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def has_valid_consent(self, patient_id: str, consent_type: str) -> bool:
        """
        Check if patient has valid, non-expired consent
        
        Args:
            patient_id: Patient ID
            consent_type: Type of consent to check
            
        Returns:
            True if valid consent exists, False otherwise
        """
        consent = self.get_consent_status(patient_id, consent_type)
        
        if not consent or not consent['granted']:
            return False
        
        # Check expiration if set
        if consent.get('expiration'):
            expiration = datetime.fromisoformat(consent['expiration'])
            if datetime.utcnow() > expiration:
                return False
        
        return True
    
    def log_model_usage(
        self,
        user_id: str,
        model_version: str,
        patient_id: Optional[str] = None,
        input_hash: Optional[str] = None,
        prediction_result: Optional[Dict[str, Any]] = None,
        confidence_score: Optional[float] = None,
        processing_time_ms: Optional[int] = None,
        decision_path: Optional[str] = None
    ):
        """
        Log AI model usage for governance and transparency
        
        Args:
            user_id: ID of user invoking model
            model_version: Version of model used
            patient_id: Optional patient ID if applicable
            input_hash: Hash of input data for audit trail
            prediction_result: Model prediction result
            confidence_score: Confidence score of prediction
            processing_time_ms: Processing time in milliseconds
            decision_path: Explainable AI decision path
        """
        with self._get_connection() as conn:
            conn.execute('''
                INSERT INTO model_usage_logs
                (timestamp, user_id, patient_id, model_version, input_hash, prediction_result, 
                 confidence_score, processing_time_ms, decision_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.utcnow().isoformat(),
                user_id,
                patient_id,
                model_version,
                input_hash,
                json.dumps(prediction_result) if prediction_result else None,
                confidence_score,
                processing_time_ms,
                decision_path
            ))
    
    def generate_audit_report(
        self,
        start_date: str,
        end_date: str,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate compliance reports for regulators
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            user_id: Optional user ID filter
            resource_type: Optional resource type filter
            
        Returns:
            List of audit log entries as dictionaries
        """
        with self._get_connection() as conn:
            query = '''
                SELECT * FROM audit_logs 
                WHERE timestamp BETWEEN ? AND ?
            '''
            params = [start_date, end_date]
            
            if user_id:
                query += ' AND user_id = ?'
                params.append(user_id)
            
            if resource_type:
                query += ' AND resource_type = ?'
                params.append(resource_type)
            
            query += ' ORDER BY timestamp DESC'
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def generate_data_access_report(
        self,
        patient_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate data access report for a specific patient (GDPR right of access)
        
        Args:
            patient_id: Patient ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of data access log entries
        """
        with self._get_connection() as conn:
            query = 'SELECT * FROM data_access_logs WHERE patient_id = ?'
            params = [patient_id]
            
            if start_date:
                query += ' AND timestamp >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND timestamp <= ?'
                params.append(end_date)
            
            query += ' ORDER BY timestamp DESC'
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_failed_access_attempts(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get failed access attempts for security monitoring
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            user_id: Optional user ID filter
            
        Returns:
            List of failed access attempts
        """
        with self._get_connection() as conn:
            query = 'SELECT * FROM data_access_logs WHERE success = 0'
            params = []
            
            if start_date:
                query += ' AND timestamp >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND timestamp <= ?'
                params.append(end_date)
            
            if user_id:
                query += ' AND user_id = ?'
                params.append(user_id)
            
            query += ' ORDER BY timestamp DESC'
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
