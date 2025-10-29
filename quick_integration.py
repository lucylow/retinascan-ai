"""
Quick integration script for the RetinaScan AI Multi-Agent System
"""
import numpy as np
from workflow_orchestrator import WorkflowOrchestrator
import threading

def demo_workflow():
    """Demonstrate the complete AI workflow system"""
    
    print("🚀 RetinaScan AI Multi-Agent System Demo")
    print("=" * 50)
    
    # Initialize the orchestrator
    # Try to use actual model path, fallback to default if not found
    model_path = "models/retina_model_final.h5"
    orchestrator = WorkflowOrchestrator(model_path)
    
    # Create sample images (in practice, load real retinal images)
    sample_images = [
        np.random.rand(512, 512, 3) * 255 for _ in range(3)
    ]
    
    print("\n🧪 Processing sample images...")
    
    # Process images sequentially
    for i, image in enumerate(sample_images):
        try:
            print(f"\n📸 Processing image {i+1}...")
            result = orchestrator.process_image(image, f"demo_{i+1}")
            
            report = result.get("final_report", {})
            diagnosis = report.get("diagnostic_findings", {})
            
            print(f"✅ Diagnosis: {diagnosis.get('primary_diagnosis', 'Unknown')}")
            print(f"📊 Confidence: {diagnosis.get('confidence_score', 0):.2%}")
            print(f"🚨 Urgency: {report.get('clinical_assessment', {}).get('urgency_level', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error processing image {i+1}: {str(e)}")
    
    # Display system performance
    print("\n" + "=" * 50)
    print("📊 SYSTEM PERFORMANCE SUMMARY")
    print("=" * 50)
    
    metrics = orchestrator.get_system_metrics()
    for agent, performance in metrics["agent_performance"].items():
        print(f"\n🤖 {agent.upper().replace('_', ' ')}:")
        print(f"   Tasks Processed: {performance['tasks_processed']}")
        print(f"   Success Rate: {performance['success_rate']:.1%}")
        print(f"   Avg Processing Time: {performance['average_processing_time']:.2f}s")
    
    if metrics['total_workflows'] > 0:
        success_rate = metrics['successful_workflows'] / metrics['total_workflows']
        print(f"\n📈 Overall System:")
        print(f"   Total Workflows: {metrics['total_workflows']}")
        print(f"   Success Rate: {success_rate:.1%}")
    else:
        print("\n📈 Overall System: No workflows completed yet")

def start_dashboard(orchestrator):
    """Start the monitoring dashboard in a separate thread"""
    try:
        from monitoring_dashboard import start_monitoring
        start_monitoring(orchestrator, port=5001)
    except ImportError as e:
        print(f"⚠️  Could not start dashboard: {e}")
        print("💡 Install Flask to enable the monitoring dashboard: pip install flask")

if __name__ == "__main__":
    # Run demo
    demo_workflow()
    
    # Uncomment to start dashboard (requires Flask)
    # orchestrator = WorkflowOrchestrator("models/retina_model_final.h5")
    # dashboard_thread = threading.Thread(target=start_dashboard, args=(orchestrator,))
    # dashboard_thread.daemon = True
    # dashboard_thread.start()
    # print("\n💡 Dashboard available at http://localhost:5001")
    # print("Press Ctrl+C to stop")
    # try:
    #     while True:
    #         threading.Event().wait(1)
    # except KeyboardInterrupt:
    #     print("\n👋 Shutting down...")
    
    print("\n🎉 Demo completed! The AI multi-agent system is ready for integration.")

