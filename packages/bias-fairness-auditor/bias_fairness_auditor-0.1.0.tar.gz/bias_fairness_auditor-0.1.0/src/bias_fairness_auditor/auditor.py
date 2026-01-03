"""Bias and fairness auditing for ML models and datasets."""

from collections import defaultdict
from itertools import combinations
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

from .types import (
    AuditConfig, AuditReport, BiasIssue, BiasType, DatasetProfile,
    FairnessMetric, GroupStats, IntersectionalAnalysis, IntersectionalGroup,
    MetricResult, MitigationStrategy, MitigationType, Severity
)


class FairnessAuditor:
    """Main class for auditing model and dataset fairness."""
    
    def __init__(self, config: Optional[AuditConfig] = None):
        """Initialize auditor.
        
        Args:
            config: Audit configuration
        """
        self.config = config
        self._custom_metrics: Dict[str, Callable] = {}
    
    def audit(self, data: List[Dict[str, Any]],
              config: Optional[AuditConfig] = None) -> AuditReport:
        """Perform full fairness audit.
        
        Args:
            data: List of data records
            config: Audit configuration (overrides default)
            
        Returns:
            Complete audit report
        """
        config = config or self.config
        if not config:
            raise ValueError("AuditConfig required")
        
        # Profile dataset
        profile = self._profile_dataset(data, config)
        
        # Calculate group statistics
        group_stats = self._calculate_group_stats(data, config)
        
        # Calculate fairness metrics
        metric_results = self._calculate_metrics(group_stats, config)
        
        # Detect bias issues
        bias_issues = self._detect_bias_issues(profile, group_stats, metric_results, config)
        
        # Intersectional analysis
        intersectional = None
        if config.intersectional and len(config.protected_attributes) > 1:
            intersectional = self._intersectional_analysis(data, config)
        
        # Generate mitigation strategies
        strategies = self._generate_mitigations(bias_issues)
        
        # Calculate overall score
        passed_count = sum(1 for m in metric_results if m.passed)
        overall_score = passed_count / len(metric_results) if metric_results else 1.0
        
        # Generate summary
        summary = self._generate_summary(metric_results, bias_issues, overall_score)
        
        return AuditReport(
            dataset_profile=profile,
            group_stats=group_stats,
            metric_results=metric_results,
            bias_issues=bias_issues,
            intersectional_analysis=intersectional,
            mitigation_strategies=strategies,
            overall_fairness_score=overall_score,
            summary=summary
        )
    
    def _profile_dataset(self, data: List[Dict], config: AuditConfig) -> DatasetProfile:
        """Profile dataset for bias analysis."""
        total = len(data)
        
        # Label distribution
        label_dist: Dict[Any, int] = defaultdict(int)
        for row in data:
            label_dist[row.get(config.label_column)] += 1
        
        # Attribute distributions
        attr_dist: Dict[str, Dict[str, int]] = {}
        for attr in config.protected_attributes:
            attr_dist[attr] = defaultdict(int)
            for row in data:
                attr_dist[attr][str(row.get(attr, "missing"))] += 1
        
        # Missing values
        missing: Dict[str, int] = {}
        for attr in config.protected_attributes + [config.label_column]:
            missing[attr] = sum(1 for row in data if row.get(attr) is None)
        
        # Imbalance ratios
        imbalance: Dict[str, float] = {}
        for attr, dist in attr_dist.items():
            if dist:
                vals = list(dist.values())
                imbalance[attr] = max(vals) / min(vals) if min(vals) > 0 else float("inf")
        
        return DatasetProfile(
            total_samples=total,
            label_distribution=dict(label_dist),
            attribute_distributions={k: dict(v) for k, v in attr_dist.items()},
            missing_values=missing,
            imbalance_ratios=imbalance
        )
    
    def _calculate_group_stats(self, data: List[Dict], 
                               config: AuditConfig) -> Dict[str, List[GroupStats]]:
        """Calculate statistics for each demographic group."""
        result: Dict[str, List[GroupStats]] = {}
        total = len(data)
        
        for attr in config.protected_attributes:
            groups: Dict[str, Dict[str, int]] = defaultdict(lambda: {
                "total": 0, "positive": 0, "negative": 0,
                "tp": 0, "fp": 0, "tn": 0, "fn": 0
            })
            
            for row in data:
                group = str(row.get(attr, "unknown"))
                label = row.get(config.label_column)
                pred = row.get(config.prediction_column) if config.prediction_column else label
                
                groups[group]["total"] += 1
                
                if label == config.favorable_label:
                    groups[group]["positive"] += 1
                else:
                    groups[group]["negative"] += 1
                
                if config.prediction_column:
                    if pred == config.favorable_label and label == config.favorable_label:
                        groups[group]["tp"] += 1
                    elif pred == config.favorable_label and label != config.favorable_label:
                        groups[group]["fp"] += 1
                    elif pred != config.favorable_label and label != config.favorable_label:
                        groups[group]["tn"] += 1
                    else:
                        groups[group]["fn"] += 1
            
            group_stats_list = []
            for name, stats in groups.items():
                n = stats["total"]
                pos = stats["positive"]
                neg = stats["negative"]
                tp = stats["tp"]
                fp = stats["fp"]
                tn = stats["tn"]
                fn = stats["fn"]
                
                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
                tnr = tn / (tn + fp) if (tn + fp) > 0 else 0.0
                fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                recall = tpr
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
                accuracy = (tp + tn) / n if n > 0 else 0.0
                
                group_stats_list.append(GroupStats(
                    name=name,
                    size=n,
                    proportion=n / total if total > 0 else 0.0,
                    positive_rate=pos / n if n > 0 else 0.0,
                    negative_rate=neg / n if n > 0 else 0.0,
                    true_positive_rate=tpr,
                    false_positive_rate=fpr,
                    true_negative_rate=tnr,
                    false_negative_rate=fnr,
                    precision=precision,
                    recall=recall,
                    f1_score=f1,
                    accuracy=accuracy
                ))
            
            result[attr] = group_stats_list
        
        return result
    
    def _calculate_metrics(self, group_stats: Dict[str, List[GroupStats]],
                          config: AuditConfig) -> List[MetricResult]:
        """Calculate fairness metrics."""
        results = []
        
        for attr in config.protected_attributes:
            groups = group_stats.get(attr, [])
            if len(groups) < 2:
                continue
            
            # Identify privileged and unprivileged groups
            privileged_val = config.privileged_groups.get(attr)
            if privileged_val:
                privileged = next((g for g in groups if g.name == str(privileged_val)), groups[0])
                unprivileged = [g for g in groups if g.name != str(privileged_val)]
            else:
                # Assume group with highest positive rate is privileged
                sorted_groups = sorted(groups, key=lambda g: g.positive_rate, reverse=True)
                privileged = sorted_groups[0]
                unprivileged = sorted_groups[1:]
            
            for unpriv in unprivileged:
                for metric in config.metrics:
                    result = self._calculate_single_metric(
                        metric, privileged, unpriv, config
                    )
                    if result:
                        results.append(result)
        
        return results
    
    def _calculate_single_metric(self, metric: FairnessMetric,
                                 privileged: GroupStats,
                                 unprivileged: GroupStats,
                                 config: AuditConfig) -> Optional[MetricResult]:
        """Calculate a single fairness metric."""
        threshold = config.thresholds.get(metric, 0.1)
        
        if metric == FairnessMetric.DEMOGRAPHIC_PARITY:
            priv_val = privileged.positive_rate
            unpriv_val = unprivileged.positive_rate
            disparity = abs(priv_val - unpriv_val)
            passed = disparity <= threshold
            interpretation = (
                f"Positive rate difference: {disparity:.3f}. "
                f"{'Acceptable' if passed else 'Exceeds'} threshold of {threshold}."
            )
            
        elif metric == FairnessMetric.DISPARATE_IMPACT:
            priv_val = privileged.positive_rate
            unpriv_val = unprivileged.positive_rate
            ratio = unpriv_val / priv_val if priv_val > 0 else 0.0
            disparity = 1 - ratio
            passed = ratio >= threshold  # Typically 0.8 (80% rule)
            interpretation = (
                f"Disparate impact ratio: {ratio:.3f}. "
                f"{'Meets' if passed else 'Fails'} 80% rule (threshold: {threshold})."
            )
            
        elif metric == FairnessMetric.EQUALIZED_ODDS:
            tpr_diff = abs(privileged.true_positive_rate - unprivileged.true_positive_rate)
            fpr_diff = abs(privileged.false_positive_rate - unprivileged.false_positive_rate)
            priv_val = (privileged.true_positive_rate + privileged.false_positive_rate) / 2
            unpriv_val = (unprivileged.true_positive_rate + unprivileged.false_positive_rate) / 2
            disparity = max(tpr_diff, fpr_diff)
            passed = disparity <= threshold
            interpretation = (
                f"Max difference in TPR/FPR: {disparity:.3f}. "
                f"{'Acceptable' if passed else 'Exceeds'} threshold of {threshold}."
            )
            
        elif metric == FairnessMetric.EQUAL_OPPORTUNITY:
            priv_val = privileged.true_positive_rate
            unpriv_val = unprivileged.true_positive_rate
            disparity = abs(priv_val - unpriv_val)
            passed = disparity <= threshold
            interpretation = (
                f"TPR difference: {disparity:.3f}. "
                f"{'Acceptable' if passed else 'Exceeds'} threshold of {threshold}."
            )
            
        elif metric == FairnessMetric.PREDICTIVE_PARITY:
            priv_val = privileged.precision
            unpriv_val = unprivileged.precision
            disparity = abs(priv_val - unpriv_val)
            passed = disparity <= threshold
            interpretation = (
                f"Precision difference: {disparity:.3f}. "
                f"{'Acceptable' if passed else 'Exceeds'} threshold of {threshold}."
            )
            
        elif metric == FairnessMetric.TREATMENT_EQUALITY:
            priv_ratio = privileged.false_negative_rate / privileged.false_positive_rate if privileged.false_positive_rate > 0 else 0
            unpriv_ratio = unprivileged.false_negative_rate / unprivileged.false_positive_rate if unprivileged.false_positive_rate > 0 else 0
            priv_val = priv_ratio
            unpriv_val = unpriv_ratio
            disparity = abs(priv_ratio - unpriv_ratio)
            passed = disparity <= threshold
            interpretation = (
                f"FN/FP ratio difference: {disparity:.3f}. "
                f"{'Acceptable' if passed else 'Exceeds'} threshold."
            )
            
        else:
            return None
        
        return MetricResult(
            metric=metric,
            value=disparity if metric != FairnessMetric.DISPARATE_IMPACT else ratio,
            threshold=threshold,
            passed=passed,
            privileged_group=privileged.name,
            unprivileged_group=unprivileged.name,
            privileged_value=priv_val,
            unprivileged_value=unpriv_val,
            disparity=disparity,
            interpretation=interpretation
        )
    
    def _detect_bias_issues(self, profile: DatasetProfile,
                           group_stats: Dict[str, List[GroupStats]],
                           metrics: List[MetricResult],
                           config: AuditConfig) -> List[BiasIssue]:
        """Detect bias issues from analysis results."""
        issues = []
        
        # Check for representation bias
        for attr, ratio in profile.imbalance_ratios.items():
            if ratio > 5:
                severity = Severity.CRITICAL if ratio > 10 else Severity.HIGH
                issues.append(BiasIssue(
                    bias_type=BiasType.REPRESENTATION,
                    attribute=attr,
                    description=f"Severe class imbalance in {attr} (ratio: {ratio:.1f}:1)",
                    severity=severity,
                    affected_groups=list(profile.attribute_distributions.get(attr, {}).keys()),
                    evidence={"imbalance_ratio": ratio},
                    recommendations=[
                        "Consider oversampling minority groups",
                        "Use stratified sampling for train/test splits",
                        "Apply class weights during training"
                    ]
                ))
        
        # Check for metric failures
        for metric in metrics:
            if not metric.passed:
                if metric.disparity > 0.3:
                    severity = Severity.CRITICAL
                elif metric.disparity > 0.2:
                    severity = Severity.HIGH
                elif metric.disparity > 0.1:
                    severity = Severity.MEDIUM
                else:
                    severity = Severity.LOW
                
                issues.append(BiasIssue(
                    bias_type=BiasType.LEARNING,
                    attribute=f"{metric.privileged_group} vs {metric.unprivileged_group}",
                    description=f"{metric.metric.value} violation: {metric.interpretation}",
                    severity=severity,
                    affected_groups=[metric.unprivileged_group],
                    evidence={
                        "metric": metric.metric.value,
                        "disparity": metric.disparity,
                        "threshold": metric.threshold
                    },
                    recommendations=self._get_metric_recommendations(metric.metric)
                ))
        
        # Check for missing data bias
        for attr, count in profile.missing_values.items():
            if count > 0:
                pct = count / profile.total_samples * 100
                if pct > 10:
                    issues.append(BiasIssue(
                        bias_type=BiasType.MEASUREMENT,
                        attribute=attr,
                        description=f"High missing value rate in {attr}: {pct:.1f}%",
                        severity=Severity.MEDIUM if pct < 20 else Severity.HIGH,
                        affected_groups=[],
                        evidence={"missing_count": count, "missing_pct": pct},
                        recommendations=[
                            "Investigate cause of missing data",
                            "Consider if missingness is related to protected attributes",
                            "Use appropriate imputation strategies"
                        ]
                    ))
        
        return issues
    
    def _get_metric_recommendations(self, metric: FairnessMetric) -> List[str]:
        """Get recommendations for a specific metric violation."""
        recommendations = {
            FairnessMetric.DEMOGRAPHIC_PARITY: [
                "Consider resampling or reweighting training data",
                "Apply threshold adjustment post-training",
                "Use adversarial debiasing techniques"
            ],
            FairnessMetric.EQUALIZED_ODDS: [
                "Apply equalized odds post-processing",
                "Use calibrated equalized odds",
                "Consider separate thresholds per group"
            ],
            FairnessMetric.EQUAL_OPPORTUNITY: [
                "Focus on equalizing true positive rates",
                "Apply threshold optimization for recall parity",
                "Review feature importance for protected attributes"
            ],
            FairnessMetric.DISPARATE_IMPACT: [
                "Review and possibly remove proxy features",
                "Apply disparate impact remover preprocessing",
                "Consider fairness constraints during training"
            ],
            FairnessMetric.PREDICTIVE_PARITY: [
                "Calibrate predictions per group",
                "Review label quality across groups",
                "Consider group-specific models"
            ]
        }
        return recommendations.get(metric, ["Review model and data for sources of bias"])
    
    def _intersectional_analysis(self, data: List[Dict],
                                 config: AuditConfig) -> IntersectionalAnalysis:
        """Perform intersectional analysis."""
        groups: Dict[str, Dict] = defaultdict(lambda: {"count": 0, "positive": 0})
        total = len(data)
        
        for row in data:
            attrs = {attr: str(row.get(attr, "unknown")) for attr in config.protected_attributes}
            key = tuple(sorted(attrs.items()))
            groups[key]["count"] += 1
            if row.get(config.label_column) == config.favorable_label:
                groups[key]["positive"] += 1
            groups[key]["attrs"] = attrs
        
        intersectional_groups = []
        for key, stats in groups.items():
            if stats["count"] > 0:
                intersectional_groups.append(IntersectionalGroup(
                    attributes=stats["attrs"],
                    size=stats["count"],
                    proportion=stats["count"] / total,
                    outcome_rate=stats["positive"] / stats["count"]
                ))
        
        if not intersectional_groups:
            return IntersectionalAnalysis(
                groups=[], most_advantaged=None, most_disadvantaged=None,
                max_disparity=0.0, significant_disparities=[]
            )
        
        sorted_groups = sorted(intersectional_groups, key=lambda g: g.outcome_rate, reverse=True)
        most_advantaged = sorted_groups[0]
        most_disadvantaged = sorted_groups[-1]
        max_disparity = most_advantaged.outcome_rate - most_disadvantaged.outcome_rate
        
        # Find significant disparities
        significant = []
        for g1, g2 in combinations(intersectional_groups, 2):
            disparity = abs(g1.outcome_rate - g2.outcome_rate)
            if disparity > 0.1:
                significant.append((g1.name, g2.name, disparity))
        
        significant.sort(key=lambda x: x[2], reverse=True)
        
        return IntersectionalAnalysis(
            groups=intersectional_groups,
            most_advantaged=most_advantaged,
            most_disadvantaged=most_disadvantaged,
            max_disparity=max_disparity,
            significant_disparities=significant[:10]
        )
    
    def _generate_mitigations(self, issues: List[BiasIssue]) -> List[MitigationStrategy]:
        """Generate mitigation strategies for detected issues."""
        strategies = []
        bias_types = {issue.bias_type for issue in issues}
        
        if BiasType.REPRESENTATION in bias_types:
            strategies.append(MitigationStrategy(
                name="Resampling",
                mitigation_type=MitigationType.PREPROCESSING,
                description="Balance dataset through oversampling minority or undersampling majority groups",
                applicable_biases=[BiasType.REPRESENTATION],
                trade_offs=["May cause overfitting", "Loss of data with undersampling"],
                implementation_complexity="Low"
            ))
        
        if BiasType.LEARNING in bias_types:
            strategies.extend([
                MitigationStrategy(
                    name="Adversarial Debiasing",
                    mitigation_type=MitigationType.INPROCESSING,
                    description="Train adversarial network to remove protected attribute information",
                    applicable_biases=[BiasType.LEARNING],
                    trade_offs=["Training complexity", "Potential accuracy trade-off"],
                    implementation_complexity="High"
                ),
                MitigationStrategy(
                    name="Threshold Optimization",
                    mitigation_type=MitigationType.POSTPROCESSING,
                    description="Adjust decision thresholds per group to achieve fairness",
                    applicable_biases=[BiasType.LEARNING],
                    trade_offs=["Requires group membership at inference"],
                    implementation_complexity="Low"
                ),
                MitigationStrategy(
                    name="Calibrated Equalized Odds",
                    mitigation_type=MitigationType.POSTPROCESSING,
                    description="Post-process predictions to satisfy equalized odds",
                    applicable_biases=[BiasType.LEARNING],
                    trade_offs=["May reduce overall accuracy"],
                    implementation_complexity="Medium"
                )
            ])
        
        if BiasType.FEATURE in bias_types or BiasType.HISTORICAL in bias_types:
            strategies.append(MitigationStrategy(
                name="Feature Engineering",
                mitigation_type=MitigationType.PREPROCESSING,
                description="Remove or transform features that encode historical bias",
                applicable_biases=[BiasType.FEATURE, BiasType.HISTORICAL],
                trade_offs=["May lose predictive power"],
                implementation_complexity="Medium"
            ))
        
        return strategies
    
    def _generate_summary(self, metrics: List[MetricResult],
                         issues: List[BiasIssue],
                         score: float) -> str:
        """Generate human-readable summary."""
        passed = sum(1 for m in metrics if m.passed)
        total = len(metrics)
        critical = sum(1 for i in issues if i.severity == Severity.CRITICAL)
        high = sum(1 for i in issues if i.severity == Severity.HIGH)
        
        status = "PASSED" if score >= 0.8 else "NEEDS ATTENTION" if score >= 0.5 else "FAILED"
        
        return (
            f"Fairness Audit: {status}\n"
            f"Overall Score: {score:.1%}\n"
            f"Metrics Passed: {passed}/{total}\n"
            f"Critical Issues: {critical}\n"
            f"High Severity Issues: {high}\n"
            f"Total Issues: {len(issues)}"
        )
    
    def register_metric(self, name: str, 
                       calculator: Callable[[GroupStats, GroupStats], MetricResult]) -> None:
        """Register a custom fairness metric."""
        self._custom_metrics[name] = calculator


class DatasetAnalyzer:
    """Analyze datasets for potential bias before training."""
    
    def analyze(self, data: List[Dict], 
                protected_attributes: List[str],
                label_column: str) -> Dict[str, Any]:
        """Analyze dataset for bias indicators.
        
        Args:
            data: Dataset as list of dicts
            protected_attributes: Columns to analyze
            label_column: Target column
            
        Returns:
            Analysis results
        """
        results = {
            "sample_count": len(data),
            "attribute_analysis": {},
            "label_correlation": {},
            "recommendations": []
        }
        
        for attr in protected_attributes:
            analysis = self._analyze_attribute(data, attr, label_column)
            results["attribute_analysis"][attr] = analysis
            
            if analysis["correlation"] > 0.3:
                results["recommendations"].append(
                    f"High correlation between {attr} and label ({analysis['correlation']:.2f})"
                )
            
            if analysis["imbalance_ratio"] > 3:
                results["recommendations"].append(
                    f"Significant imbalance in {attr} (ratio: {analysis['imbalance_ratio']:.1f})"
                )
        
        return results
    
    def _analyze_attribute(self, data: List[Dict], attr: str, 
                          label_column: str) -> Dict[str, Any]:
        """Analyze a single attribute."""
        groups: Dict[str, Dict] = defaultdict(lambda: {"count": 0, "positive": 0})
        
        for row in data:
            group = str(row.get(attr, "missing"))
            groups[group]["count"] += 1
            if row.get(label_column) == 1:
                groups[group]["positive"] += 1
        
        counts = [g["count"] for g in groups.values()]
        imbalance = max(counts) / min(counts) if min(counts) > 0 else float("inf")
        
        # Simple correlation approximation
        rates = [g["positive"] / g["count"] if g["count"] > 0 else 0 for g in groups.values()]
        correlation = max(rates) - min(rates) if rates else 0
        
        return {
            "unique_values": len(groups),
            "distribution": {k: v["count"] for k, v in groups.items()},
            "positive_rates": {k: v["positive"] / v["count"] if v["count"] > 0 else 0 
                             for k, v in groups.items()},
            "imbalance_ratio": imbalance,
            "correlation": correlation
        }


class FairnessComparator:
    """Compare fairness across multiple models."""
    
    def compare(self, data: List[Dict],
                predictions: Dict[str, List[Any]],
                config: AuditConfig) -> Dict[str, Any]:
        """Compare fairness metrics across models.
        
        Args:
            data: Original data
            predictions: Dict of model_name -> predictions
            config: Audit configuration
            
        Returns:
            Comparison results
        """
        auditor = FairnessAuditor()
        results = {}
        
        for model_name, preds in predictions.items():
            # Add predictions to data
            augmented_data = []
            for i, row in enumerate(data):
                new_row = dict(row)
                new_row[config.prediction_column or "prediction"] = preds[i]
                augmented_data.append(new_row)
            
            # Audit with predictions
            pred_config = AuditConfig(
                protected_attributes=config.protected_attributes,
                label_column=config.label_column,
                prediction_column=config.prediction_column or "prediction",
                favorable_label=config.favorable_label,
                privileged_groups=config.privileged_groups,
                metrics=config.metrics,
                thresholds=config.thresholds
            )
            
            report = auditor.audit(augmented_data, pred_config)
            results[model_name] = {
                "score": report.overall_fairness_score,
                "passed": report.passed,
                "metrics": {m.metric.value: m.value for m in report.metric_results},
                "issues": len(report.bias_issues)
            }
        
        # Find best model
        best_model = max(results.keys(), key=lambda k: results[k]["score"])
        
        return {
            "model_results": results,
            "best_model": best_model,
            "best_score": results[best_model]["score"]
        }
