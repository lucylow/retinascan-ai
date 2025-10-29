import React from 'react';
import { WorkflowStatus } from '../../services/aiAgentService';

interface WorkflowResultsProps {
  workflow?: WorkflowStatus;
}

export const WorkflowResults: React.FC<WorkflowResultsProps> = ({ workflow }) => {
  if (!workflow) {
    return (
      <div className="results-placeholder">
        <div className="placeholder-icon">🔍</div>
        <p>Select a workflow to view results</p>
      </div>
    );
  }

  if (workflow.status === 'running') {
    return (
      <div className="results-processing">
        <div className="processing-animation">
          <div className="ai-brain">🧠</div>
          <div className="pulse-ring"></div>
          <div className="pulse-ring delay-1"></div>
          <div className="pulse-ring delay-2"></div>
        </div>
        <h3>AI Analysis in Progress</h3>
        <p>Multiple AI agents are analyzing the retina image...</p>
        <div className="agent-activities">
          <div className="agent-activity">
            <span className="agent-emoji">📊</span>
            <span>Data Processor: Enhancing image quality</span>
          </div>
          <div className="agent-activity">
            <span className="agent-emoji">🤖</span>
            <span>AI Specialist: Analyzing retinal features</span>
          </div>
          <div className="agent-activity">
            <span className="agent-emoji">🔍</span>
            <span>Diagnosis Analyst: Reviewing findings</span>
          </div>
        </div>
      </div>
    );
  }

  if (workflow.status === 'failed') {
    return (
      <div className="results-error">
        <div className="error-icon">❌</div>
        <h3>Analysis Failed</h3>
        <p>{workflow.error || 'Unknown error occurred during processing'}</p>
        <button className="retry-button" onClick={() => window.location.reload()}>
          Retry Analysis
        </button>
      </div>
    );
  }

  if (workflow.status === 'completed' && workflow.result) {
    const report = workflow.result.final_report || workflow.result;
    const diagnosis = report.diagnostic_findings || {};
    const clinical = report.clinical_assessment || {};
    const recommendations = report.recommendations || {};

    return (
      <div className="results-completed">
        <div className="results-header">
          <h3>Diagnostic Report</h3>
          <div className="report-actions">
            <button className="btn-secondary">📥 Download PDF</button>
            <button className="btn-primary">🔄 Share with Specialist</button>
          </div>
        </div>

        <div className="diagnosis-summary">
          <div className={`diagnosis-card ${clinical.urgency_level || 'unknown'}`}>
            <div className="diagnosis-main">
              <h4>{diagnosis.primary_diagnosis || 'Unknown Diagnosis'}</h4>
              <div className="confidence-badge">
                Confidence: {((diagnosis.confidence_score || 0) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="urgency-indicator">
              <span className={`urgency-badge ${clinical.urgency_level || 'unknown'}`}>
                {(clinical.urgency_level || 'UNKNOWN').toUpperCase()} PRIORITY
              </span>
            </div>
          </div>
        </div>

        <div className="clinical-details">
          <div className="detail-section">
            <h5>Clinical Assessment</h5>
            <div className="detail-grid">
              <div className="detail-item">
                <span className="detail-label">Severity Level</span>
                <span className="detail-value">{diagnosis.severity_level !== undefined ? `${diagnosis.severity_level}/4` : 'N/A'}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Quality Score</span>
                <span className="detail-value">{clinical.quality_assessment || 'N/A'}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Recommended Follow-up</span>
                <span className="detail-value">{recommendations.follow_up_timeline || 'N/A'}</span>
              </div>
            </div>
          </div>

          {clinical.risk_factors && clinical.risk_factors.length > 0 && (
            <div className="detail-section">
              <h5>Risk Factors Identified</h5>
              <div className="risk-factors">
                {clinical.risk_factors.map((factor: string, index: number) => (
                  <div key={index} className="risk-factor">
                    <span className="risk-icon">⚠️</span>
                    {factor}
                  </div>
                ))}
              </div>
            </div>
          )}

          {recommendations.immediate_actions && recommendations.immediate_actions.length > 0 && (
            <div className="detail-section">
              <h5>Immediate Recommendations</h5>
              <div className="recommendations">
                {recommendations.immediate_actions.map((action: string, index: number) => (
                  <div key={index} className="recommendation">
                    <span className="check-icon">✅</span>
                    {action}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="technical-details">
          <h5>Technical Information</h5>
          <div className="tech-grid">
            <div className="tech-item">
              <span>Workflow ID</span>
              <span>{workflow.id}</span>
            </div>
            <div className="tech-item">
              <span>Processing Time</span>
              <span>{workflow.endTime && workflow.startTime 
                ? `${((workflow.endTime.getTime() - workflow.startTime.getTime()) / 1000).toFixed(2)}s`
                : 'N/A'}</span>
            </div>
            <div className="tech-item">
              <span>Report ID</span>
              <span>{report.report_id || 'N/A'}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

