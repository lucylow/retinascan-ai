# Bias & Fairness Framework for RetinaScan AI

## Overview

This comprehensive bias and fairness framework ensures that RetinaScan AI delivers equitable healthcare outcomes across all patient demographics. The system addresses bias detection, mitigation, continuous monitoring, and regulatory compliance.

## 🎯 Key Features

### 1. Diverse Dataset Management
- **Multi-source datasets**: Integrates APTOS (India), EyePACS (USA), Messidor (France), and RFMiD (multi-country)
- **Demographic balancing**: Ensures minimum 5% representation per demographic group
- **Gap identification**: Automatically detects underrepresented groups and triggers data collection

### 2. Continuous Fairness Auditing
- **Real-time monitoring**: Daily audits of model performance across demographic subgroups
- **Comprehensive metrics**: Tracks accuracy, sensitivity, specificity, false positive/negative rates, demographic parity, and equalized odds
- **Bias flag detection**: Automatic detection of high/medium/low severity bias issues

### 3. Bias Mitigation Strategies
- **Reweighting**: Adjusts sample weights based on demographic representation
- **Oversampling**: Augments underrepresented groups with synthetic data
- **Adversarial debiasing**: Removes protected attribute information from predictions
- **Fairness-regularized loss**: Penalizes unfair predictions during training

### 4. Transparency & Reporting
- **Comprehensive reports**: Executive summaries, detailed analysis, and demographic breakdowns
- **Regulatory compliance**: FDA, EU MDR, and HIPAA compliance checking
- **Public dashboard**: Real-time fairness metrics visible to stakeholders

## 📁 File Structure

### Frontend (TypeScript/React)

```
src/
├── types/
│   └── fairness.ts                    # Type definitions for fairness metrics, bias flags, etc.
├── services/
│   ├── DatasetManager.ts              # Diverse dataset loading and balancing
│   ├── FairnessAuditor.ts             # Continuous bias monitoring and auditing
│   ├── BiasMitigation.ts              # Bias mitigation strategies
│   └── TransparencyReporter.ts        # Fairness reporting and dashboard updates
├── components/
│   └── Fairness/
│       └── FairnessMonitor.tsx        # React component for UI display
└── pages/
    └── FairnessPage.tsx               # Main fairness monitoring page
```

### Backend (Python)

```
services/
├── fairness_evaluator.py              # Backend fairness metrics calculation
└── dataset_manager.py                 # Backend dataset management
```

## 🔧 Usage

### Frontend Integration

1. **Access the Fairness Monitor**:
   Navigate to `/fairness` in the application to view the fairness dashboard.

2. **Programmatic Usage**:
```typescript
import { FairnessAuditor } from '@/services/FairnessAuditor';
import { DatasetManager } from '@/services/DatasetManager';

// Load diverse datasets
const datasetManager = new DatasetManager();
await datasetManager.loadDiverseDatasets();

// Perform fairness audit
const auditor = new FairnessAuditor();
const audit = await auditor.performComprehensiveAudit(
  predictions,
  testData,
  demographicGroups
);
```

### Backend Integration

```python
from services.fairness_evaluator import FairnessEvaluator
import numpy as np

# Initialize evaluator
evaluator = FairnessEvaluator()

# Define demographic groups (boolean masks)
demographic_groups = {
    'White': white_mask,
    'Black': black_mask,
    'Asian': asian_mask,
    # ... more groups
}

# Perform audit
audit_result = evaluator.perform_comprehensive_audit(
    predictions=np.array(predictions),
    labels=np.array(labels),
    demographic_groups=demographic_groups
)

# Access results
metrics = audit_result['metrics']
bias_flags = audit_result['bias_flags']
recommendations = audit_result['recommendations']
```

## 📊 Fairness Metrics

### Core Metrics

1. **Accuracy**: Overall prediction accuracy
2. **Sensitivity (TPR)**: True positive rate - ability to detect DR when present
3. **Specificity (TNR)**: True negative rate - ability to correctly identify no DR
4. **False Positive Rate (FPR)**: Rate of false alarms
5. **False Negative Rate (FNR)**: Rate of missed diagnoses

### Fairness-Specific Metrics

1. **Demographic Parity**: Proportion of positive predictions should be similar across groups
2. **Equalized Odds**: True positive and false positive rates should be similar across groups
3. **Predictive Parity**: Positive predictive value should be similar across groups
4. **Equal Opportunity**: True positive rate should be similar across groups

## 🚨 Bias Detection

The system automatically detects bias using the following thresholds:

- **Demographic Parity**: < 0.8 → High severity flag
- **Equalized Odds**: < 0.85 → Medium severity flag
- **False Positive Rate**: > 0.2 → High severity flag
- **False Negative Rate**: > 0.2 → High severity flag
- **Accuracy Disparity**: > 0.15 → Medium severity flag

## 🛡️ Bias Mitigation

### 1. Reweighting
Automatically adjusts sample weights during training to balance representation:
```typescript
import { BiasMitigationStrategies } from '@/services/BiasMitigation';

const { weights, augmentedData } = BiasMitigationStrategies.applyReweighting(
  trainingData,
  labels
);
```

### 2. Oversampling
Augments underrepresented groups with synthetic data:
```typescript
const augmentedData = BiasMitigationStrategies.applyOversampling(trainingData);
```

### 3. Fairness-Regularized Loss
Incorporates fairness constraints into the training loss:
```typescript
const FairnessLoss = BiasMitigationStrategies.createFairnessRegularizedLoss([
  { type: 'demographic_parity', threshold: 0.8, protectedAttributes: ['race'] },
  { type: 'equalized_odds', threshold: 0.85, protectedAttributes: ['race', 'gender'] }
]);
```

## 📈 Monitoring & Reporting

### Continuous Monitoring

The system performs daily audits and alerts on bias detection:

```typescript
const auditor = new FairnessAuditor();
await auditor.continuousMonitoring(
  () => model,
  async () => await getProductionData(),
  async () => await getDemographicGroups()
);
```

### Report Generation

```typescript
import { TransparencyReporter } from '@/services/TransparencyReporter';

const reporter = new TransparencyReporter();
const report = await reporter.generateFairnessReport(auditResult);

// Report includes:
// - Executive summary
// - Detailed analysis
// - Demographic breakdown
// - Bias mitigation history
// - Recommendations
// - Regulatory compliance status
```

## ✅ Regulatory Compliance

The framework automatically checks compliance with:

1. **FDA**: Requires accuracy > 80% and no high-severity bias flags
2. **EU MDR**: Requires equalized odds > 80%
3. **HIPAA**: Always compliant (data privacy, not model fairness)

## 🔄 Workflow

1. **Dataset Loading**: Load diverse datasets from multiple sources
2. **Balanced Splitting**: Ensure balanced representation in training data
3. **Model Training**: Apply fairness-aware training with bias mitigation
4. **Fairness Auditing**: Continuous monitoring of model performance
5. **Bias Detection**: Automatic flagging of unfair predictions
6. **Mitigation**: Application of corrective strategies
7. **Reporting**: Generation of comprehensive fairness reports
8. **Compliance**: Verification of regulatory requirements

## 📚 References

This implementation is based on best practices from:
- PMC articles on healthcare AI bias (PMC11785882, PMC8996038)
- Nature publications on autonomous AI for diabetic retinopathy
- PLOS Digital Health articles on bias mitigation
- CDC guidelines on health equity

## 🎯 Best Practices

1. **Diverse Data**: Always use multi-ethnic, multicenter datasets
2. **Regular Audits**: Perform fairness audits at least monthly
3. **Stratified Analysis**: Always analyze performance by demographic subgroup
4. **Transparency**: Publish fairness metrics publicly
5. **Community Engagement**: Work with patient advocacy groups
6. **Continuous Improvement**: Iteratively improve based on audit findings

## 🚀 Next Steps

To fully deploy this framework:

1. **Connect Real Data**: Replace mock data with actual patient datasets
2. **Implement Model Integration**: Connect to actual model inference pipeline
3. **Set Up Alerts**: Configure alerting system for bias detection
4. **Dashboard Deployment**: Deploy public-facing fairness dashboard
5. **Regulatory Submission**: Use reports for FDA/EU MDR submissions

## 📞 Support

For questions or issues with the bias and fairness framework, please refer to the main project documentation or contact the development team.
