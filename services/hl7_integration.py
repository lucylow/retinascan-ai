"""
HL7 v2 Integration for Legacy EHR Systems
Provides MLLP-based message exchange for HL7 v2 compliant systems
"""
import socket
import ssl
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)


class HL7v2Integration:
    """HL7 v2 integration for legacy EHR systems"""
    
    def __init__(self, host: str, port: int, use_tls: bool = True):
        self.host = host
        self.port = port
        self.use_tls = use_tls
        self.socket_timeout = 30
    
    def create_adt_message(self, message_type: str, patient_data: Dict, 
                         ai_result: Dict = None) -> str:
        """Create HL7 v2 ADT message"""
        
        # Message Header
        msh = self._create_msh_segment(message_type)
        
        # Event Type
        evn = self._create_evn_segment(message_type)
        
        # Patient Identification
        pid = self._create_pid_segment(patient_data)
        
        # Observation Result (if AI result provided)
        obx_segments = []
        if ai_result:
            obx_segments = self._create_obx_segments(ai_result)
        
        # Combine all segments
        segments = [msh, evn, pid] + obx_segments
        message = '\r'.join(segments) + '\r'
        
        return message
    
    def _create_msh_segment(self, message_type: str) -> str:
        """Create MSH (Message Header) segment"""
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        message_control_id = str(uuid.uuid4())[:20]
        
        msh_fields = [
            'MSH',
            '^~\\&',
            'RETINASCAN_AI',
            'AI_CLINIC',
            'EHR_SYSTEM',
            'HOSPITAL',
            timestamp,
            '',
            f'ADT^{message_type}',
            message_control_id,
            'P',
            '2.5'
        ]
        
        return '|'.join(msh_fields)
    
    def _create_evn_segment(self, message_type: str) -> str:
        """Create EVN (Event Type) segment"""
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        evn_fields = [
            'EVN',
            message_type,
            timestamp,
            '',
            '',
            'RETINASCAN_AI^AI System^^^'
        ]
        
        return '|'.join(evn_fields)
    
    def _create_pid_segment(self, patient_data: Dict) -> str:
        """Create PID (Patient Identification) segment"""
        
        pid_fields = [
            'PID',
            '1',
            patient_data.get('patient_id', ''),
            '',
            f"{patient_data.get('last_name', '')}^{patient_data.get('first_name', '')}",
            '',
            patient_data.get('birth_date', '').replace('-', ''),
            patient_data.get('gender', 'U'),
            '',
            '',
            patient_data.get('address', ''),
            '',
            patient_data.get('phone', ''),
            '',
            '',
            '',
            '',
            patient_data.get('account_number', ''),
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            ''
        ]
        
        return '|'.join(pid_fields)
    
    def _create_obx_segments(self, ai_result: Dict) -> List[str]:
        """Create OBX (Observation/Result) segments for AI results"""
        
        segments = []
        
        # Main diagnosis observation
        obx1_fields = [
            'OBX',
            '1',
            'ST',
            '81204-9^Diabetic Retinopathy Screening^LN',
            '',
            ai_result.get('diagnosis', 'Unknown'),
            '',
            '',
            '',
            'F',
            '',
            datetime.now().strftime('%Y%m%d%H%M%S'),
            '',
            'RETINASCAN_AI^AI System'
        ]
        segments.append('|'.join(obx1_fields))
        
        # Severity level
        obx2_fields = [
            'OBX',
            '2',
            'NM',
            '81205-6^Diabetic Retinopathy Severity Scale^LN',
            '',
            str(ai_result.get('severity_level', 0)),
            '',
            '',
            '',
            'F',
            '',
            datetime.now().strftime('%Y%m%d%H%M%S'),
            '',
            'RETINASCAN_AI^AI System'
        ]
        segments.append('|'.join(obx2_fields))
        
        # Confidence score
        obx3_fields = [
            'OBX',
            '3',
            'NM',
            'AI-CONFIDENCE^AI Confidence Score^L',
            '',
            f"{ai_result.get('confidence', 0):.3f}",
            '',
            '',
            '',
            'F',
            '',
            datetime.now().strftime('%Y%m%d%H%M%S'),
            '',
            'RETINASCAN_AI^AI System'
        ]
        segments.append('|'.join(obx3_fields))
        
        # Recommendation
        obx4_fields = [
            'OBX',
            '4',
            'ST',
            'AI-RECOMMEND^AI Recommendation^L',
            '',
            ai_result.get('recommendation', ''),
            '',
            '',
            '',
            'F',
            '',
            datetime.now().strftime('%Y%m%d%H%M%S'),
            '',
            'RETINASCAN_AI^AI System'
        ]
        segments.append('|'.join(obx4_fields))
        
        return segments
    
    def send_hl7_message(self, message: str) -> Dict:
        """Send HL7 v2 message via MLLP"""
        
        try:
            # Wrap message in MLLP frame
            mllp_message = f'\x0B{message}\x1C\r'
            
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.socket_timeout)
            
            if self.use_tls:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                sock = context.wrap_socket(sock, server_hostname=self.host)
            
            # Connect and send
            sock.connect((self.host, self.port))
            sock.sendall(mllp_message.encode('utf-8'))
            
            # Receive response
            response = b''
            while True:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                response += chunk
                if b'\x1C\r' in response:  # MLLP end of message
                    break
            
            sock.close()
            
            # Parse response
            ack_success = self._parse_ack_response(response.decode('utf-8'))
            
            return {
                'success': ack_success,
                'response': response.decode('utf-8'),
                'message_control_id': self._extract_message_control_id(message)
            }
            
        except Exception as e:
            logger.error(f"HL7 message sending failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_ack_response(self, response: str) -> bool:
        """Parse HL7 ACK response"""
        
        if not response.startswith('\x0BMSH'):
            return False
        
        lines = response.split('\r')
        for line in lines:
            if line.startswith('MSA'):
                fields = line.split('|')
                if len(fields) >= 2:
                    ack_code = fields[1]
                    return ack_code == 'AA'
        
        return False
    
    def _extract_message_control_id(self, message: str) -> str:
        """Extract message control ID from MSH segment"""
        
        lines = message.split('\r')
        for line in lines:
            if line.startswith('MSH'):
                fields = line.split('|')
                if len(fields) >= 10:
                    return fields[9]
        
        return ''


class HL7MessageBuilder:
    """Builder for various HL7 message types"""
    
    @staticmethod
    def create_adt_a04(patient_data: Dict, ai_result: Dict = None) -> str:
        """Create ADT^A04 (Register a patient) message"""
        
        hl7_integration = HL7v2Integration('dummy', 0)
        return hl7_integration.create_adt_message('A04', patient_data, ai_result)
    
    @staticmethod
    def create_adt_a08(patient_data: Dict, ai_result: Dict) -> str:
        """Create ADT^A08 (Update patient information) message"""
        
        hl7_integration = HL7v2Integration('dummy', 0)
        return hl7_integration.create_adt_message('A08', patient_data, ai_result)
    
    @staticmethod
    def create_orm_o01(patient_data: Dict, ai_result: Dict) -> str:
        """Create ORM^O01 (Order message) for referral"""
        
        base_message = HL7MessageBuilder.create_adt_a08(patient_data, ai_result)
        
        # Add order segments
        orc_segment = 'ORC|NW|REF12345|||||||||||||RETINASCAN_AI'
        obr_segment = 'OBR|1|REF12345||81204-9^Diabetic Retinopathy Screening^LN|||||||||||||||||||||||||||||||||||||'
        
        return base_message + '\r' + orc_segment + '\r' + obr_segment

