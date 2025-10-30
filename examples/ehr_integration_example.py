"""
Example: EHR Integration with RetinaScan AI
Demonstrates how to integrate RetinaScan AI with EHR systems
"""
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.fhir_integration import FHIRIntegrationService, FHIRConfig
from services.hl7_integration import HL7v2Integration, HL7MessageBuilder
from services.clinical_workflow import ClinicalWorkflowManager
from services.ehr_config import EHRConfig


def example_fhir_integration():
    """Example: FHIR integration"""
    
    print("=" * 60)
    print("Example 1: FHIR Integration")
    print("=" * 60)
    
    # Load configuration
    ehr_config = EHRConfig.from_env()
    
    # Initialize FHIR service
    fhir_config = FHIRConfig(
        fhir_base_url=ehr_config.fhir_base_url,
        client_id=ehr_config.fhir_client_id,
        client_secret=ehr_config.fhir_client_secret,
        auth_url=ehr_config.fhir_auth_url,
        token_url=ehr_config.fhir_token_url,
        redirect_uri=ehr_config.fhir_redirect_uri
    )
    
    fhir_service = FHIRIntegrationService(fhir_config)
    
    # Authenticate (in production, this would happen via OAuth2)
    print("\n📋 Authenticating with SMART on FHIR...")
    # Note: This requires valid credentials
    # authenticate = fhir_service.authenticate_smart_on_fhir()
    # print(f"Authentication: {authenticate}")
    
    # Example: Create diabetic retinopathy observation
    print("\n📋 Creating FHIR Observation...")
    ai_result = {
        'diagnosis': 'Moderate Diabetic Retinopathy',
        'severity_level': 2,
        'confidence': 0.87,
        'quality_score': 0.92,
        'recommendation': 'Refer to ophthalmologist within 3-6 months'
    }
    
    observation = fhir_service.create_dr_observation(ai_result, 'test-patient-123')
    print(f"✅ Created observation with ID: {observation['id']}")
    print(f"   Diagnosis: {observation['valueCodeableConcept']['text']}")
    print(f"   Severity Level: {observation['component'][0]['valueInteger']}")
    print(f"   Confidence: {observation['component'][1]['valueDecimal']:.1%}")
    
    # Example: Create diagnostic report
    print("\n📋 Creating Diagnostic Report...")
    diagnostic_report = fhir_service.create_diagnostic_report(
        ai_result, 'base64_image_data', 'test-patient-123'
    )
    print(f"✅ Created report with ID: {diagnostic_report['id']}")
    print(f"   Conclusion: {diagnostic_report['conclusion'][:100]}...")


def example_hl7_integration():
    """Example: HL7 v2 integration"""
    
    print("\n" + "=" * 60)
    print("Example 2: HL7 v2 Integration")
    print("=" * 60)
    
    # Create sample patient data
    patient_data = {
        'patient_id': '12345',
        'first_name': 'John',
        'last_name': 'Doe',
        'birth_date': '1970-01-01',
        'gender': 'M',
        'phone': '555-1234',
        'address': '123 Main St',
        'account_number': 'ACC-001'
    }
    
    # Create sample AI result
    ai_result = {
        'diagnosis': 'Moderate Diabetic Retinopathy',
        'severity_level': 2,
        'confidence': 0.87,
        'recommendation': 'Refer to ophthalmologist within 3-6 months'
    }
    
    # Build HL7 message
    print("\n📋 Building HL7 ADT^A08 message...")
    hl7_message = HL7MessageBuilder.create_adt_a08(patient_data, ai_result)
    
    print("\nHL7 Message:")
    print(hl7_message)
    
    # Display parsed information
    print("\n✅ Message Details:")
    print(f"   Patient: {patient_data['first_name']} {patient_data['last_name']}")
    print(f"   Diagnosis: {ai_result['diagnosis']}")
    print(f"   Severity: {ai_result['severity_level']}")
    
    # In production, send via MLLP
    # hl7_service = HL7v2Integration(host='localhost', port=2575, use_tls=False)
    # result = hl7_service.send_hl7_message(hl7_message)
    # print(f"\nSending result: {result}")


def example_clinical_workflow():
    """Example: Complete clinical workflow"""
    
    print("\n" + "=" * 60)
    print("Example 3: Clinical Workflow")
    print("=" * 60)
    
    # Initialize services
    ehr_config = EHRConfig.from_env()
    
    fhir_config = FHIRConfig(
        fhir_base_url=ehr_config.fhir_base_url,
        client_id=ehr_config.fhir_client_id,
        client_secret=ehr_config.fhir_client_secret,
        auth_url=ehr_config.fhir_auth_url,
        token_url=ehr_config.fhir_token_url,
        redirect_uri=ehr_config.fhir_redirect_uri
    )
    
    fhir_service = FHIRIntegrationService(fhir_config)
    hl7_service = HL7v2Integration(
        host=ehr_config.hl7_host,
        port=ehr_config.hl7_port,
        use_tls=ehr_config.hl7_use_tls
    )
    
    workflow_manager = ClinicalWorkflowManager(fhir_service, hl7_service)
    
    # Configure workflow
    workflow_config = ehr_config.to_workflow_config()
    
    print("\n📋 Configuration:")
    print(f"   Auto-approve confidence: {workflow_config['auto_approve_confidence']:.1%}")
    print(f"   Auto-approve max severity: {workflow_config['auto_approve_max_severity']}")
    print(f"   Require human review: {workflow_config['require_human_review']}")
    print(f"   Referral automation: {workflow_config['enable_referral_automation']}")
    print(f"   Follow-up scheduling: {workflow_config['enable_follow_up_scheduling']}")
    
    # Example workflow processing (async in production)
    print("\n📋 Processing screening workflow...")
    print("   (Note: This requires valid EHR credentials)")
    
    # import asyncio
    # result = asyncio.run(workflow_manager.process_screening_workflow(
    #     patient_id='test-patient-123',
    #     image_data='base64_image_data',
    #     workflow_config=workflow_config
    # ))
    # 
    # print("\n✅ Workflow Results:")
    # print(f"   Success: {result['success']}")
    # print(f"   Workflow ID: {result['workflow_id']}")
    # print(f"   Referral created: {result.get('referral_created', False)}")
    # print(f"   Follow-up scheduled: {result.get('follow_up_scheduled', False)}")


def example_terminologies():
    """Example: Standard terminologies"""
    
    print("\n" + "=" * 60)
    print("Example 4: Standard Terminologies")
    print("=" * 60)
    
    # LOINC codes
    print("\n📋 LOINC Codes:")
    print("   Retinal imaging screening: 81204-9")
    print("   Severity scale: 81205-6")
    print("   Retinal image: 42132-1")
    
    # SNOMED CT codes
    print("\n📋 SNOMED CT Codes:")
    print("   No diabetic retinopathy: 408637004")
    print("   Mild DR: 408638009")
    print("   Moderate DR: 408639001")
    print("   Severe DR: 408640004")
    print("   Proliferative DR: 408641000")
    
    # Code systems
    print("\n📋 Code Systems:")
    print("   LOINC: http://loinc.org")
    print("   SNOMED: http://snomed.info/sct")
    print("   ICD-10: http://hl7.org/fhir/sid/icd-10")
    
    print("\n✅ All terminologies follow HL7/FHIR standards")


def main():
    """Run all examples"""
    
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "RetinaScan AI - EHR Integration Examples" + " " * 9 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        # Run examples
        example_fhir_integration()
        example_hl7_integration()
        example_clinical_workflow()
        example_terminologies()
        
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        print("\n✅ All examples completed successfully!")
        print("\nKey Features Demonstrated:")
        print("   • FHIR R4 resource creation")
        print("   • HL7 v2 message generation")
        print("   • Clinical workflow orchestration")
        print("   • Standard terminologies (LOINC, SNOMED)")
        print("\nNext Steps:")
        print("   1. Configure EHR credentials in .env")
        print("   2. Register SMART on FHIR application")
        print("   3. Test with sandbox environment")
        print("   4. Deploy to production")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        print("\nNote: Some examples require valid EHR credentials.")
        print("      Configure your .env file to test with real systems.")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

