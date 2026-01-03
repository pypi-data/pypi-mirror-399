"""Type definitions for bias-fairness-auditor."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class FairnessMetric(Enum):
    """Fairness metrics."""
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    PREDICTIVE_PARITY = "predictive_parity"
    CALIBRATION = "calibration"
    TREATMENT_EQUALITY = "treatment_equality"
    DISPARATE_IMPACT = "disparate_impact"
    STATISTICAL_PARITY = "statistical_parity"


class BiasType(Enum):
    """Types of bias."""
    REPRESENTATION = "representation"
    MEASUREMENT = "measurement"
    AGGREGATION = "aggregation"
    LEARNING = "learning"
    EVALUATION = "evaluation"
    HISTORICAL = "historical"
    SELECTION = "selection"
    LABEL = "label"
    FEATURE = "feature"


class Severity(Enum):
    """Bias severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MitigationType(Enum):
    """Bias mitigation strategies."""
    PREPROCESSING = "preprocessing"
    INPROCESSING = "inprocessing"
    POSTPROCESSING = "postprocessing"


@dataclass
class GroupStats:
    """Statistics for a demographic group."""
    name: str
    size: int
    proportion: float
    positive_rate: float
    negative_rate: float
    true_positive_rate: float = 0.0
    false_positive_rate: float = 0.0
    true_negative_rate: float = 0.0
    false_negative_rate: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    accuracy: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "size": self.size,
            "proportion": self.proportion,
            "positive_rate": self.positive_rate,
            "true_positive_rate": self.true_positive_rate,
            "false_positive_rate": self.false_positive_rate,
            "precision": self.precision,
            "recall": self.recall,
            "accuracy": self.accuracy
        }


@dataclass
class MetricResult:
    """Result of a fairness metric calculation."""
    metric: FairnessMetric
    value: float
    threshold: float
    passed: bool
    privileged_group: str
    unprivileged_group: str
    privileged_value: float
    unprivileged_value: float
    disparity: float
    interpretation: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric": self.metric.value,
            "value": self.value,
            "threshold": self.threshold,
            "passed": self.passed,
            "privileged_group": self.privileged_group,
            "unprivileged_group": self.unprivileged_group,
            "disparity": self.disparity,
            "interpretation": self.interpretation
        }


@dataclass
class BiasIssue:
    """A detected bias issue."""
    bias_type: BiasType
    attribute: str
    description: str
    severity: Severity
    affected_groups: List[str]
    evidence: Dict[str, Any]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "bias_type": self.bias_type.value,
            "attribute": self.attribute,
            "description": self.description,
            "severity": self.severity.value,
            "affected_groups": self.affected_groups,
            "evidence": self.evidence,
            "recommendations": self.recommendations
        }


@dataclass
class IntersectionalGroup:
    """An intersectional demographic group."""
    attributes: Dict[str, str]
    size: int
    proportion: float
    outcome_rate: float
    
    @property
    def name(self) -> str:
        return " & ".join(f"{k}={v}" for k, v in self.attributes.items())


@dataclass
class IntersectionalAnalysis:
    """Results of intersectional analysis."""
    groups: List[IntersectionalGroup]
    most_advantaged: Optional[IntersectionalGroup]
    most_disadvantaged: Optional[IntersectionalGroup]
    max_disparity: float
    significant_disparities: List[Tuple[str, str, float]]


@dataclass
class MitigationStrategy:
    """A bias mitigation strategy."""
    name: str
    mitigation_type: MitigationType
    description: str
    applicable_biases: List[BiasType]
    trade_offs: List[str]
    implementation_complexity: str


@dataclass
class AuditConfig:
    """Configuration for fairness audit."""
    protected_attributes: List[str]
    label_column: str
    prediction_column: Optional[str] = None
    favorable_label: Any = 1
    unfavorable_label: Any = 0
    privileged_groups: Dict[str, Any] = field(default_factory=dict)
    metrics: List[FairnessMetric] = field(default_factory=lambda: [
        FairnessMetric.DEMOGRAPHIC_PARITY,
        FairnessMetric.EQUALIZED_ODDS,
        FairnessMetric.DISPARATE_IMPACT
    ])
    thresholds: Dict[FairnessMetric, float] = field(default_factory=lambda: {
        FairnessMetric.DEMOGRAPHIC_PARITY: 0.1,
        FairnessMetric.EQUALIZED_ODDS: 0.1,
        FairnessMetric.EQUAL_OPPORTUNITY: 0.1,
        FairnessMetric.DISPARATE_IMPACT: 0.8,
        FairnessMetric.PREDICTIVE_PARITY: 0.1,
    })
    intersectional: bool = False


@dataclass
class DatasetProfile:
    """Profile of a dataset for bias analysis."""
    total_samples: int
    label_distribution: Dict[Any, int]
    attribute_distributions: Dict[str, Dict[str, int]]
    missing_values: Dict[str, int]
    imbalance_ratios: Dict[str, float]


@dataclass
class AuditReport:
    """Complete fairness audit report."""
    dataset_profile: DatasetProfile
    group_stats: Dict[str, List[GroupStats]]
    metric_results: List[MetricResult]
    bias_issues: List[BiasIssue]
    intersectional_analysis: Optional[IntersectionalAnalysis] = None
    mitigation_strategies: List[MitigationStrategy] = field(default_factory=list)
    overall_fairness_score: float = 0.0
    summary: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_profile": {
                "total_samples": self.dataset_profile.total_samples,
                "label_distribution": self.dataset_profile.label_distribution,
                "imbalance_ratios": self.dataset_profile.imbalance_ratios
            },
            "group_stats": {
                attr: [g.to_dict() for g in groups]
                for attr, groups in self.group_stats.items()
            },
            "metric_results": [m.to_dict() for m in self.metric_results],
            "bias_issues": [b.to_dict() for b in self.bias_issues],
            "overall_fairness_score": self.overall_fairness_score,
            "summary": self.summary
        }
    
    @property
    def passed(self) -> bool:
        """Check if all metrics passed."""
        return all(m.passed for m in self.metric_results)
    
    @property
    def critical_issues(self) -> List[BiasIssue]:
        """Get critical bias issues."""
        return [i for i in self.bias_issues if i.severity == Severity.CRITICAL]
