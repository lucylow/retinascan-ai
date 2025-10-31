# Healthcare Interoperability Implementation Guide
## RetinaScan AI - Practical Implementation

**Purpose:** Step-by-step guide to implementing interoperability enhancements

---

## Quick Start: Priority 1 Improvements

### 1. Data Quality Framework

#### Implementation Steps

**Step 1: Install Required Dependencies**
```bash
pip install great-expectations pandas jsonschema pydantic validators
```

**Step 2: Create Quality Framework Structure**
```bash
mkdir -p services/data_quality
touch services/data_quality/__init__.py
touch services/data_quality/quality_engine.py
touch services/data_quality/rules.py
touch services/data_quality/scoring.py
```

**Step 3: Implement Core Quality Engine**

Create `services/data_quality/quality_engine.py`:
```python
"""
Data Quality Engine - Central quality assessment framework
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class QualityResult:
    """Result of a quality check"""
    rule_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    issues: List[str] = field(default_factory=list)
    auto_fixable: bool = False
    fix_suggestion: Optional[str] = None


@dataclass
class QualityReport:
    """Comprehensive quality assessment report"""
    timestamp: datetime
    overall_score: float
    dimension_scores: Dict[str, float]
    results: List[QualityResult]
    auto_fixed: bool = False
    recommendation: Optional[str] = None
    
    def add_recommendation(self):
        """Generate recommendation based on scores"""
        if self.overall_score < 0.7:
            self.recommendation = "Data quality is poor. Manual review required."
        elif self.overall_score < 0.9:
            self.recommendation = "Data quality acceptable but could be improved."
        else:
            self.recommendation = "Data quality is excellent."


class QualityRule:
    """Abstract base class for quality rules"""
    
    def __init__(self, name: str, dimension: str):
        self.name = name
        self.dimension = dimension
    
    async def validate(self, data: Dict, context: Dict) -> QualityResult:
        """
        Validate data against this rule
        
        Args:
            data: Data to validate
            context: Additional context (required fields, etc.)
        
        Returns:
            QualityResult with validation outcome
        """
        raise NotImplementedError("Subclasses must implement validate()")


class QualityEngine:
    """Main quality assessment engine"""
    
    def __init__(self, rules: List[QualityRule]):
        self.rules = rules
    
    async def assess(self, data: Dict, context: Optional[Dict] = None) -> QualityReport:
        """
        Assess data quality using all configured rules
        
        Args:
            data: Data to assess
            context: Optional context for validation
        
        Returns:
            QualityReport with detailed results
        """
        context = context or {}
        
        # Run all validation rules
        results = await asyncio.gather(*[
            rule.validate(data, context)
            for rule in self.rules
        ])
        
        # Calculate scores
        overall_score = self._calculate_overall_score(results)
        dimension_scores = self._calculate_dimension_scores(results)
        
        # Create report
        report = QualityReport(
            timestamp=datetime.now(),
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            results=results
        )
        report.add_recommendation()
        
        # Log quality assessment
        logger.info(f"Quality assessment: {overall_score:.2%} - {report.recommendation}")
        
        return report
    
    def _calculate_overall_score(self, results: List[QualityResult]) -> float:
        """Calculate overall quality score"""
        if not results:
            return 1.0
        
        total_score = sum(r.score for r in results)
        return total_score / len(results)
    
    def _calculate_dimension_scores(self, results: List[QualityResult]) -> Dict[str, float]:
        """Calculate scores per quality dimension"""
        dimension_scores = {}
        
        for result in results:
            dim = result.dimension
            if dim not in dimension_scores:
                dimension_scores[dim] = []
            dimension_scores[dim].append(result.score)
        
        # Average scores per dimension
        return {
            dim: sum(scores) / len(scores)
            for dim, scores in dimension_scores.items()
        }
    
    async def auto_correct(self, data: Dict, results: List[QualityResult]) -> Dict:
        """
        Automatically correct fixable issues
        
        Args:
            data: Original data
            results: Quality check results
        
        Returns:
            Corrected data
        """
        corrected = data.copy()
        
        for result in results:
            if result.auto_fixable and result.fix_suggestion:
                # Apply fix
                logger.info(f"Auto-correcting: {result.rule_name}")
                corrected = self._apply_fix(corrected, result.fix_suggestion)
        
        return corrected
    
    def _apply_fix(self, data: Dict, fix: str) -> Dict:
        """Apply fix suggestion to data"""
        # Implementation would parse fix and apply it
        # This is a placeholder
        return data
```

**Step 4: Implement Quality Rules**

Create `services/data_quality/rules.py`:
```python
"""
Quality validation rules for healthcare data
"""
from typing import Dict, List
from .quality_engine import QualityRule, QualityResult
import re


class CompletenessRule(QualityRule):
    """Check if required fields are present"""
    
    async def validate(self, data: Dict, context: Dict) -> QualityResult:
        required_fields = context.get('required_fields', [])
        
        missing = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                missing.append(field)
        
        # Score based on percentage of fields present
        score = 1.0 if not required_fields else (len(required_fields) - len(missing)) / len(required_fields)
        
        issues = [f"Missing required field: {f}" for f in missing]
        
        return QualityResult(
            rule_name="completeness_check",
            passed=len(missing) == 0,
            score=score,
            issues=issues,
            auto_fixable=False
        )


class FormatRule(QualityRule):
    """Check data format compliance"""
    
    def __init__(self, field: str, pattern: str, name: str = None):
        super().__init__(name or f"format_check_{field}", "format")
        self.field = field
        self.pattern = pattern
    
    async def validate(self, data: Dict, context: Dict) -> QualityResult:
        value = data.get(self.field)
        
        if value is None:
            return QualityResult(
                rule_name=self.name,
                passed=True,  # Don't fail if missing (completeness handles that)
                score=1.0,
                issues=[]
            )
        
        # Validate against pattern
        is_valid = bool(re.match(self.pattern, str(value)))
        
        return QualityResult(
            rule_name=self.name,
            passed=is_valid,
            score=1.0 if is_valid else 0.0,
            issues=[] if is_valid else [f"{self.field} format is invalid"],
            auto_fixable=False
        )


class RangeRule(QualityRule):
    """Check if numeric values are within acceptable range"""
    
    def __init__(self, field: str, min_val: float, max_val: float, name: str = None):
        super().__init__(name or f"range_check_{field}", "range")
        self.field = field
        self.min_val = min_val
        self.max_val = max_val
    
    async def validate(self, data: Dict, context: Dict) -> QualityResult:
        value = data.get(self.field)
        
        if value is None:
            return QualityResult(
                rule_name=self.name,
                passed=True,
                score=1.0,
                issues=[]
            )
        
        try:
            num_value = float(value)
            is_valid = self.min_val <= num_value <= self.max_val
            
            return QualityResult(
                rule_name=self.name,
                passed=is_valid,
                score=1.0 if is_valid else 0.5,
                issues=[] if is_valid else [f"{self.field} out of range: [{self.min_val}, {self.max_val}]"],
                auto_fixable=False
            )
        except ValueError:
            return QualityResult(
                rule_name=self.name,
                passed=False,
                score=0.0,
                issues=[f"{self.field} is not numeric"],
                auto_fixable=False
            )


class ConsistencyRule(QualityRule):
    """Check data consistency (e.g., codes match values)"""
    
    async def validate(self, data: Dict, context: Dict) -> QualityResult:
        issues = []
        
        # Example: Check if confidence is consistent with certainty level
        confidence = data.get('confidence', 0.0)
        severity = data.get('severity_level', 0)
        
        # High severity + low confidence is suspicious
        if severity >= 3 and confidence < 0.7:
            issues.append("High severity with low confidence - inconsistent")
        
        # Very low confidence should not have certain diagnosis
        if confidence < 0.5 and data.get('diagnosis') != 'No Diabetic Retinopathy':
            issues.append("Very low confidence with abnormal diagnosis - inconsistent")
        
        score = 1.0 if not issues else 0.5
        
        return QualityResult(
            rule_name="consistency_check",
            passed=len(issues) == 0,
            score=score,
            issues=issues,
            auto_fixable=False
        )


class ClinicalLogicRule(QualityRule):
    """Apply clinical logic rules"""
    
    async def validate(self, data: Dict, context: Dict) -> QualityResult:
        issues = []
        severity = data.get('severity_level', 0)
        diagnosis = data.get('diagnosis', '')
        
        # Check if severity level matches diagnosis
        severity_map = {
            'No Diabetic Retinopathy': 0,
            'Mild Diabetic Retinopathy': 1,
            'Moderate Diabetic Retinopathy': 2,
            'Severe Diabetic Retinopathy': 3,
            'Proliferative Diabetic Retinopathy': 4
        }
        
        expected_severity = severity_map.get(diagnosis, -1)
        if expected_severity != -1 and severity != expected_severity:
            issues.append(f"Diagnosis '{diagnosis}' suggests severity {expected_severity}, but got {severity}")
        
        score = 1.0 if not issues else 0.7
        
        return QualityResult(
            rule_name="clinical_logic_check",
            passed=len(issues) == 0,
            score=score,
            issues=issues,
            auto_fixable=False
        )


def get_default_rules() -> List[QualityRule]:
    """Get default quality rules for RetinaScan AI"""
    
    return [
        CompletenessRule("completeness_check", "completeness"),
        FormatRule("patient_id", r"^[A-Z0-9-]+$", "patient_id_format"),
        RangeRule("confidence", 0.0, 1.0, "confidence_range"),
        RangeRule("quality_score", 0.0, 1.0, "quality_score_range"),
        RangeRule("severity_level", 0, 4, "severity_range"),
        ConsistencyRule("consistency_check", "consistency"),
        ClinicalLogicRule("clinical_logic_check", "clinical_logic")
    ]
```

**Step 5: Integrate with Clinical Workflow**

Update `services/clinical_workflow.py`:
```python
# Add import
from services.data_quality.quality_engine import QualityEngine
from services.data_quality.rules import get_default_rules

# In __init__
def __init__(self, fhir_service, hl7_service):
    self.fhir_service = fhir_service
    self.hl7_service = hl7_service
    self.workflow_states = {}
    self.audit_log = []
    
    # Initialize quality engine
    self.quality_engine = QualityEngine(get_default_rules())

# Add quality check to workflow
async def _perform_ai_analysis(self, image_data: str, patient_data: Dict) -> Dict:
    """Perform AI analysis with quality validation"""
    
    # ... existing AI analysis code ...
    
    # Add quality assessment
    quality_report = await self.quality_engine.assess(
        ai_result,
        context={
            'required_fields': ['diagnosis', 'severity_level', 'confidence'],
            'patient_id': patient_data.get('patient_id')
        }
    )
    
    # Log quality metrics
    self.audit_log.append({
        'type': 'quality_assessment',
        'score': quality_report.overall_score,
        'dimensions': quality_report.dimension_scores,
        'issues': [r.issues for r in quality_report.results if r.issues]
    })
    
    # Add quality score to result
    ai_result['quality_assessment'] = {
        'overall_score': quality_report.overall_score,
        'passed': all(r.passed for r in quality_report.results),
        'issues': quality_report.recommendation
    }
    
    return ai_result
```

---

### 2. Code Mapping Service

#### Implementation Steps

**Step 1: Install Dependencies**
```bash
pip install pyarrow pandas requests
```

**Step 2: Create Code Mapping Structure**
```bash
mkdir -p services/code_mapping
touch services/code_mapping/__init__.py
touch services/code_mapping/mapper.py
touch services/code_mapping/terminology_server.py
```

**Step 3: Implement Code Mapper**

Create `services/code_mapping/mapper.py`:
```python
"""
Code mapping and translation service
"""
from typing import Dict, Optional, List
import logging
import json

logger = logging.getLogger(__name__)


class CodeMappingService:
    """Service for healthcare code translation and mapping"""
    
    def __init__(self, mappings_file: str = "data/code_mappings.json"):
        self.mappings = self._load_mappings(mappings_file)
        self.fallback_mappings = self._create_fallback_mappings()
    
    def _load_mappings(self, filepath: str) -> Dict:
        """Load code mappings from file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Mappings file not found: {filepath}. Using defaults.")
            return {}
    
    def _create_fallback_mappings(self) -> Dict:
        """Create default fallback mappings for RetinaScan"""
        return {
            # SNOMED to ICD-10 mappings
            '408637004': 'E11.329',  # No DR
            '408638009': 'E11.329',  # Mild DR
            '408639001': 'E11.329',  # Moderate DR
            '408640004': 'E11.36',   # Severe DR
            '408641000': 'E11.36',   # PDR
            
            # Severity level to codes
            'severity_0': '408637004',
            'severity_1': '408638009',
            'severity_2': '408639001',
            'severity_3': '408640004',
            'severity_4': '408641000'
        }
    
    async def translate_code(self, 
                           source_code: str,
                           source_system: str,
                           target_system: str,
                           version: Optional[str] = None) -> Optional[str]:
        """
        Translate code from one system to another
        
        Args:
            source_code: Code to translate
            source_system: Source code system (snomed, icd10, loinc, etc.)
            target_system: Target code system
            version: Optional version string
        
        Returns:
            Translated code or None if no mapping found
        """
        key = f"{source_system}:{source_code}"
        
        # Try full mapping first
        mapping = self.mappings.get(key, {})
        translated = mapping.get(target_system)
        
        if translated:
            logger.info(f"Translated {source_code} from {source_system} to {target_system}: {translated}")
            return translated
        
        # Try fallback mappings
        translated = self.fallback_mappings.get(source_code)
        if translated:
            logger.info(f"Used fallback mapping for {source_code}: {translated}")
            return translated
        
        # Log warning if no mapping found
        logger.warning(f"No mapping found for {key} to {target_system}")
        return None
    
    async def validate_code(self, code: str, system: str) -> Dict:
        """
        Validate code against known valid codes
        
        Args:
            code: Code to validate
            system: Code system
        
        Returns:
            Validation result with version and status
        """
        valid_codes = {
            'snomed': ['408637004', '408638009', '408639001', '408640004', '408641000'],
            'loinc': ['81204-9', '81205-6', '42132-1'],
            'severity': ['0', '1', '2', '3', '4']
        }
        
        is_valid = code in valid_codes.get(system, [])
        
        return {
            'code': code,
            'system': system,
            'is_valid': is_valid,
            'version': self._get_code_version(code, system),
            'deprecated': False
        }
    
    def _get_code_version(self, code: str, system: str) -> str:
        """Get version information for a code"""
        # In production, would query terminology server
        return "2024-01"
    
    async def get_code_display(self, code: str, system: str) -> Optional[str]:
        """Get human-readable display name for code"""
        displays = {
            'snomed': {
                '408637004': 'No diabetic retinopathy',
                '408638009': 'Mild non-proliferative diabetic retinopathy',
                '408639001': 'Moderate non-proliferative diabetic retinopathy',
                '408640004': 'Severe non-proliferative diabetic retinopathy',
                '408641000': 'Proliferative diabetic retinopathy'
            },
            'severity': {
                '0': 'No Diabetic Retinopathy',
                '1': 'Mild Diabetic Retinopathy',
                '2': 'Moderate Diabetic Retinopathy',
                '3': 'Severe Diabetic Retinopathy',
                '4': 'Proliferative Diabetic Retinopathy'
            }
        }
        
        return displays.get(system, {}).get(code)
    
    async def create_fhir_coding(self, code: str, system: str) -> Dict:
        """Create FHIR Coding object from code and system"""
        display = await self.get_code_display(code, system)
        
        system_urls = {
            'snomed': 'http://snomed.info/sct',
            'loinc': 'http://loinc.org',
            'icd10': 'http://hl7.org/fhir/sid/icd-10'
        }
        
        return {
            'system': system_urls.get(system, system),
            'code': code,
            'display': display or code
        }
```

**Step 4: Integrate with FHIR Service**

Update `services/fhir_integration.py`:
```python
# Add import
from services.code_mapping.mapper import CodeMappingService

# In __init__
def __init__(self, config: FHIRConfig):
    self.config = config
    self.access_token = None
    self.token_expiry = None
    self.patient_context = None
    self.encryption_key = Fernet.generate_key()
    self.cipher_suite = Fernet(self.encryption_key)
    
    # Initialize code mapping service
    self.code_mapper = CodeMappingService()
    
    # ... existing code ...

# Update code creation to use mapper
def create_dr_observation(self, ai_result: Dict, patient_id: str = None) -> Dict:
    """Create FHIR Observation with proper code mapping"""
    
    # ... existing code ...
    
    # Get diagnosis code using mapper
    diagnosis = ai_result.get('diagnosis', 'Unknown')
    snomed_code = await self.code_mapper.translate_code(
        source_code=f"severity_{ai_result.get('severity_level', 0)}",
        source_system='severity',
        target_system='snomed'
    )
    
    # Create proper coding
    coding = await self.code_mapper.create_fhir_coding(snomed_code, 'snomed')
    
    # ... rest of observation creation ...
```

---

## Integration with Existing Services

### Update Clinical Workflow

Modify `services/clinical_workflow.py` to include quality checks:

```python
from services.data_quality.quality_engine import QualityEngine
from services.data_quality.rules import get_default_rules

class ClinicalWorkflowManager:
    def __init__(self, fhir_service, hl7_service):
        # ... existing init ...
        
        # Add quality engine
        self.quality_engine = QualityEngine(get_default_rules())
    
    async def _perform_ai_analysis(self, image_data: str, patient_data: Dict) -> Dict:
        """Perform AI analysis with quality validation"""
        
        # Get AI result (your existing logic)
        ai_result = {
            'diagnosis': 'Moderate Diabetic Retinopathy',
            'severity_level': 2,
            'confidence': 0.87,
            'quality_score': 0.92
        }
        
        # Quality assessment
        quality_report = await self.quality_engine.assess(
            ai_result,
            context={
                'required_fields': ['diagnosis', 'severity_level', 'confidence'],
                'patient_id': patient_data.get('patient_id')
            }
        )
        
        # Add quality metadata
        ai_result['quality_metadata'] = {
            'overall_score': quality_report.overall_score,
            'dimensions': quality_report.dimension_scores,
            'passed': all(r.passed for r in quality_report.results),
            'issues': [issue for r in quality_report.results for issue in r.issues]
        }
        
        return ai_result
```

---

## Configuration & Deployment

### Environment Variables

Add to `.env`:
```bash
# Data Quality Settings
ENABLE_DATA_QUALITY=true
DATA_QUALITY_THRESHOLD=0.8
AUTO_FIX_QUALITY_ISSUES=true

# Code Mapping Settings
CODE_MAPPINGS_FILE=data/code_mappings.json
ENABLE_CODE_VALIDATION=true
TERMINOLOGY_SERVER_URL=https://terminology.fhir.org

# Quality Monitoring
QUALITY_MONITORING_ENABLED=true
QUALITY_DASHBOARD_URL=http://localhost:3000/quality
```

### Configuration Updates

Update `services/ehr_config.py`:
```python
@dataclass
class DataQualityConfig:
    """Data quality configuration"""
    enabled: bool = True
    threshold: float = 0.8
    auto_fix: bool = True
    required_dimensions: List[str] = None
    
    def __post_init__(self):
        if self.required_dimensions is None:
            self.required_dimensions = ['completeness', 'format', 'consistency']
```

---

## Testing

### Quality Engine Tests

Create `tests/test_data_quality.py`:
```python
"""Tests for data quality framework"""
import pytest
from services.data_quality.quality_engine import QualityEngine
from services.data_quality.rules import get_default_rules


@pytest.mark.asyncio
async def test_completeness_check():
    engine = QualityEngine(get_default_rules())
    
    # Test complete data
    complete_data = {
        'diagnosis': 'Moderate Diabetic Retinopathy',
        'severity_level': 2,
        'confidence': 0.87
    }
    
    report = await engine.assess(complete_data, {'required_fields': ['diagnosis', 'severity_level', 'confidence']})
    assert report.overall_score > 0.9
    assert all(r.passed for r in report.results if r.rule_name == 'completeness_check')


@pytest.mark.asyncio
async def test_range_validation():
    engine = QualityEngine(get_default_rules())
    
    # Test out of range
    invalid_data = {
        'diagnosis': 'No Diabetic Retinopathy',
        'severity_level': 2,
        'confidence': 1.5  # Out of range
    }
    
    report = await engine.assess(invalid_data, {})
    
    # Should have issues
    range_results = [r for r in report.results if r.rule_name == 'confidence_range']
    assert len(range_results) > 0
    assert any(not r.passed for r in range_results)


@pytest.mark.asyncio
async def test_consistency_check():
    engine = QualityEngine(get_default_rules())
    
    # Test inconsistent data
    inconsistent_data = {
        'diagnosis': 'Severe Diabetic Retinopathy',
        'severity_level': 3,
        'confidence': 0.5  # Too low for severe
    }
    
    report = await engine.assess(inconsistent_data, {})
    
    consistency_results = [r for r in report.results if r.rule_name == 'consistency_check']
    assert any(not r.passed for r in consistency_results)
```

---

## Next Steps

1. **Implement Priority 1 Features** (Data Quality + Code Mapping)
2. **Create Vendor Adapters** (Phase 2)
3. **Build Multi-Source Integration** (Phase 2)
4. **Deploy Compliance Monitoring** (Phase 2)

Refer to `INTEROPERABILITY_ASSESSMENT.md` for full roadmap.

---

## Support

- Documentation: See `EHR_INTEGRATION_GUIDE.md`
- Architecture: See `ARCHITECTURE.md`
- Assessment: See `INTEROPERABILITY_ASSESSMENT.md`
- Issues: Check GitHub issues or contact dev team

