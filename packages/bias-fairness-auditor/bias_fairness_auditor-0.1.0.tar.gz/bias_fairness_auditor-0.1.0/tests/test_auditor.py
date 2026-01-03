"""Tests for Bias & Fairness Auditor."""

import pytest
from bias_fairness_auditor import (
    FairnessAuditor,
    FairnessCalculator,
    DataBiasDetector,
    ModelBiasAuditor,
    BiasMitigator,
    AuditConfig,
    FairnessMetric,
    BiasType,
    ProtectedAttribute,
    MitigationType,
    SeverityLevel,
    ComplianceStandard,
)


class TestFairnessCalculator:
    """Test FairnessCalculator class."""
    
    def test_demographic_parity_equal(self):
        """Test demographic parity with equal rates."""
        calc = FairnessCalculator()
        ratio, diff = calc.demographic_parity(0.5, 0.5)
        assert ratio == 1.0
        assert diff == 0.0
    
    def test_demographic_parity_unequal(self):
        """Test demographic parity with unequal rates."""
        calc = FairnessCalculator()
        ratio, diff = calc.demographic_parity(0.8, 0.4)
        assert ratio == 0.5
        assert diff == -0.4
    
    def test_disparate_impact(self):
        """Test disparate impact calculation."""
        calc = FairnessCalculator()
        
        # Fair case (80% rule satisfied)
        di = calc.disparate_impact(0.5, 0.45)
        assert di >= 0.8
        
        # Unfair case
        di = calc.disparate_impact(0.8, 0.3)
        assert di < 0.8
    
    def test_equalized_odds(self):
        """Test equalized odds calculation."""
        calc = FairnessCalculator()
        tpr_diff, fpr_diff = calc.equalized_odds(0.8, 0.75, 0.1, 0.15)
        
        assert tpr_diff == 0.05
        assert fpr_diff == 0.05
    
    def test_equal_opportunity(self):
        """Test equal opportunity calculation."""
        calc = FairnessCalculator()
        diff = calc.equal_opportunity(0.9, 0.85)
        assert diff == pytest.approx(0.05)
    
    def test_predictive_parity(self):
        """Test predictive parity calculation."""
        calc = FairnessCalculator()
        diff = calc.predictive_parity(0.7, 0.65)
        assert diff == pytest.approx(0.05)
    
    def test_theil_index_equal(self):
        """Test Theil index with equal distribution."""
        calc = FairnessCalculator()
        benefits = [1.0, 1.0, 1.0, 1.0]
        theil = calc.theil_index(benefits)
        assert theil == 0.0
    
    def test_theil_index_unequal(self):
        """Test Theil index with unequal distribution."""
        calc = FairnessCalculator()
        benefits = [1.0, 2.0, 3.0, 4.0]
        theil = calc.theil_index(benefits)
        assert theil > 0


class TestDataBiasDetector:
    """Test DataBiasDetector class."""
    
    def test_detect_representation_bias(self):
        """Test detection of representation bias."""
        detector = DataBiasDetector()
        
        # Imbalanced data
        data = [{"gender": "M", "approved": True}] * 90 + \
               [{"gender": "F", "approved": True}] * 10
        
        report = detector.analyze(data, "approved", ["gender"])
        
        assert len(report.bias_instances) > 0
        assert any(
            b.bias_type == BiasType.REPRESENTATION_BIAS 
            for b in report.bias_instances
        )
    
    def test_detect_label_correlation(self):
        """Test detection of label correlation."""
        detector = DataBiasDetector()
        
        data = [
            {"gender": "M", "approved": True},
            {"gender": "M", "approved": True},
            {"gender": "F", "approved": False},
            {"gender": "F", "approved": False},
        ]
        
        report = detector.analyze(data, "approved", ["gender"])
        
        assert "gender" in report.label_correlations
    
    def test_empty_data(self):
        """Test handling of empty data."""
        detector = DataBiasDetector()
        report = detector.analyze([], "label", [])
        
        assert report.sample_size == 0
        assert len(report.bias_instances) == 0


class TestModelBiasAuditor:
    """Test ModelBiasAuditor class."""
    
    def test_audit_fair_model(self):
        """Test auditing a fair model."""
        auditor = ModelBiasAuditor()
        
        predictions = [1, 0, 1, 0, 1, 0, 1, 0]
        actuals = [1, 0, 1, 0, 1, 0, 1, 0]
        protected = {"gender": ["M", "M", "F", "F", "M", "M", "F", "F"]}
        
        report = auditor.audit(predictions, actuals, protected)
        
        assert report.overall_fairness_score > 0
    
    def test_audit_unfair_model(self):
        """Test auditing an unfair model."""
        auditor = ModelBiasAuditor()
        
        # Predictions favor one group
        predictions = [1, 1, 1, 1, 0, 0, 0, 0]
        actuals = [1, 1, 0, 0, 1, 1, 0, 0]
        protected = {"gender": ["M", "M", "M", "M", "F", "F", "F", "F"]}
        
        report = auditor.audit(predictions, actuals, protected)
        
        # Should detect fairness issues
        assert len(report.fairness_scores) > 0
    
    def test_group_metrics_calculated(self):
        """Test that group metrics are calculated."""
        auditor = ModelBiasAuditor()
        
        predictions = [1, 0, 1, 0]
        actuals = [1, 0, 1, 1]
        protected = {"attr": ["A", "A", "B", "B"]}
        
        report = auditor.audit(predictions, actuals, protected)
        
        assert len(report.group_metrics) == 2


class TestBiasMitigator:
    """Test BiasMitigator class."""
    
    def test_reweighting(self):
        """Test reweighting mitigation."""
        mitigator = BiasMitigator()
        
        data = [
            {"gender": "M"},
            {"gender": "M"},
            {"gender": "M"},
            {"gender": "F"},
        ]
        labels = [True, True, False, False]
        
        result = mitigator.mitigate(
            MitigationType.REWEIGHTING,
            data, labels, "gender"
        )
        
        assert result.success
        assert "weights" in result.metadata
        assert len(result.metadata["weights"]) == 4
    
    def test_resampling(self):
        """Test resampling mitigation."""
        mitigator = BiasMitigator()
        
        data = [{"gender": "M"}] * 10 + [{"gender": "F"}] * 2
        labels = [True] * 8 + [False] * 2 + [True, False]
        
        result = mitigator.mitigate(
            MitigationType.RESAMPLING,
            data, labels, "gender"
        )
        
        assert result.success
        assert "resampled_indices" in result.metadata
    
    def test_threshold_optimization(self):
        """Test threshold optimization."""
        mitigator = BiasMitigator()
        
        data = [{"gender": "M"}, {"gender": "M"}, {"gender": "F"}, {"gender": "F"}]
        labels = [True, False, True, False]
        predictions = [0.8, 0.3, 0.7, 0.4]
        
        result = mitigator.mitigate(
            MitigationType.THRESHOLD_OPTIMIZER,
            data, labels, "gender",
            predictions=predictions
        )
        
        assert result.success
        assert "optimal_thresholds" in result.metadata


class TestFairnessAuditor:
    """Test main FairnessAuditor class."""
    
    def test_create_auditor(self):
        """Test creating auditor."""
        auditor = FairnessAuditor()
        assert auditor is not None
    
    def test_create_with_config(self):
        """Test creating auditor with config."""
        config = AuditConfig(
            protected_attributes=[ProtectedAttribute.GENDER],
            privileged_groups={},
            unprivileged_groups={},
            fairness_threshold=0.9
        )
        
        auditor = FairnessAuditor(config)
        assert auditor.config.fairness_threshold == 0.9
    
    def test_audit_data(self):
        """Test data auditing."""
        auditor = FairnessAuditor()
        
        data = [
            {"gender": "M", "outcome": True},
            {"gender": "F", "outcome": False},
        ]
        
        report = auditor.audit_data(data, "outcome", ["gender"])
        
        assert report.sample_size == 2
    
    def test_audit_model(self):
        """Test model auditing."""
        auditor = FairnessAuditor()
        
        report = auditor.audit_model(
            predictions=[1, 0, 1, 0],
            actuals=[1, 0, 1, 1],
            protected_attributes={"g": ["A", "A", "B", "B"]}
        )
        
        assert len(report.fairness_scores) > 0
    
    def test_full_audit(self):
        """Test full audit pipeline."""
        auditor = FairnessAuditor()
        
        data = [
            {"gender": "M", "label": True},
            {"gender": "M", "label": True},
            {"gender": "F", "label": False},
            {"gender": "F", "label": True},
        ]
        predictions = [1, 1, 0, 1]
        
        result = auditor.full_audit(
            data=data,
            label_column="label",
            predictions=predictions,
            protected_columns=["gender"]
        )
        
        assert result.data_report is not None
        assert result.model_report is not None
        assert result.executive_summary != ""


class TestEnums:
    """Test enum values."""
    
    def test_fairness_metrics(self):
        """Test fairness metric enum."""
        assert FairnessMetric.DEMOGRAPHIC_PARITY.value == "demographic_parity"
        assert FairnessMetric.DISPARATE_IMPACT.value == "disparate_impact"
    
    def test_bias_types(self):
        """Test bias type enum."""
        assert BiasType.SELECTION_BIAS.value == "selection_bias"
        assert BiasType.PROXY_BIAS.value == "proxy_bias"
    
    def test_severity_levels(self):
        """Test severity level enum."""
        assert SeverityLevel.CRITICAL.value == "critical"
        assert SeverityLevel.LOW.value == "low"
    
    def test_mitigation_types(self):
        """Test mitigation type enum."""
        assert MitigationType.REWEIGHTING.value == "reweighting"
        assert MitigationType.THRESHOLD_OPTIMIZER.value == "threshold_optimizer"


class TestEdgeCases:
    """Test edge cases."""
    
    def test_single_group(self):
        """Test with single protected group."""
        auditor = ModelBiasAuditor()
        
        predictions = [1, 0, 1, 0]
        actuals = [1, 0, 1, 0]
        protected = {"gender": ["M", "M", "M", "M"]}
        
        report = auditor.audit(predictions, actuals, protected)
        
        # Should handle gracefully
        assert report is not None
    
    def test_empty_predictions(self):
        """Test with empty predictions."""
        auditor = ModelBiasAuditor()
        
        report = auditor.audit([], [], {})
        
        assert report.overall_fairness_score == 1.0
    
    def test_all_same_predictions(self):
        """Test with all same predictions."""
        auditor = ModelBiasAuditor()
        
        predictions = [1, 1, 1, 1]
        actuals = [1, 1, 0, 0]
        protected = {"g": ["A", "A", "B", "B"]}
        
        report = auditor.audit(predictions, actuals, protected)
        
        assert report is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
