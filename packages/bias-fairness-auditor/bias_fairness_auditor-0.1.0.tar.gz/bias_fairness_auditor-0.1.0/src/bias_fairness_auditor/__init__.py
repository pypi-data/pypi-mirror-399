"""
Bias & Fairness Auditor

Production-ready ML fairness auditing with bias detection and mitigation.
"""

from .types import (
    FairnessMetric,
    BiasType,
    ProtectedAttribute,
    MitigationType,
    SeverityLevel,
    ComplianceStandard,
    ProtectedGroup,
    GroupMetrics,
    FairnessScore,
    BiasInstance,
    DataBiasReport,
    ModelBiasReport,
    MitigationResult,
    ComplianceResult,
    IntersectionalAnalysis,
    ExplanationResult,
    AuditConfig,
    AuditResult,
    MonitoringAlert,
    MonitoringConfig,
)

from .auditor import (
    FairnessCalculator,
    DataBiasDetector,
    ModelBiasAuditor,
    BiasMitigator,
    ComplianceChecker,
    FairnessAuditor,
)

__version__ = "0.1.0"
__author__ = "Pranay M"

__all__ = [
    # Enums
    "FairnessMetric",
    "BiasType",
    "ProtectedAttribute",
    "MitigationType",
    "SeverityLevel",
    "ComplianceStandard",
    # Data classes
    "ProtectedGroup",
    "GroupMetrics",
    "FairnessScore",
    "BiasInstance",
    "DataBiasReport",
    "ModelBiasReport",
    "MitigationResult",
    "ComplianceResult",
    "IntersectionalAnalysis",
    "ExplanationResult",
    "AuditConfig",
    "AuditResult",
    "MonitoringAlert",
    "MonitoringConfig",
    # Core classes
    "FairnessCalculator",
    "DataBiasDetector",
    "ModelBiasAuditor",
    "BiasMitigator",
    "ComplianceChecker",
    "FairnessAuditor",
]
