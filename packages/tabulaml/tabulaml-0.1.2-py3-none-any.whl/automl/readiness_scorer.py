"""
Production Readiness Scoring Module

Evaluates model readiness for production deployment based on:
- Data quality (class balance, missing values)
- Leakage risk (suspicious features)
- Model stability (CV vs Test performance gap)
- Feature reliability (importance distribution)
- Overall deployment risk
"""

import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from .leakage_detector import LeakageReport, LeakageRisk


class ReadinessLevel(Enum):
    """Production readiness levels."""
    READY = "ready"                    # Good to deploy
    READY_WITH_CAUTION = "caution"     # Deploy with monitoring
    NEEDS_REVIEW = "review"            # Requires human review
    NOT_READY = "not_ready"            # Do not deploy


@dataclass
class ScoreComponent:
    """A single scoring component."""
    name: str
    score: float  # 0-100
    weight: float  # Component weight
    status: str
    details: str
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ReadinessScore:
    """Complete production readiness assessment."""
    overall_score: float  # 0-100
    readiness_level: ReadinessLevel
    components: List[ScoreComponent] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    @property
    def is_deployable(self) -> bool:
        return self.readiness_level in [ReadinessLevel.READY, ReadinessLevel.READY_WITH_CAUTION]


class ReadinessScorer:
    """
    Scores model readiness for production deployment.

    Components:
    1. Data Quality Score (20%)
    2. Leakage Risk Score (25%)
    3. Model Stability Score (25%)
    4. Feature Reliability Score (15%)
    5. Performance Score (15%)
    """

    # Component weights (should sum to 1.0)
    WEIGHTS = {
        'data_quality': 0.20,
        'leakage_risk': 0.25,
        'model_stability': 0.25,
        'feature_reliability': 0.15,
        'performance': 0.15
    }

    def __init__(
        self,
        min_samples: int = 100,
        max_imbalance_ratio: float = 10.0,
        max_cv_test_gap: float = 0.15,
        min_acceptable_score: float = 0.6
    ):
        """
        Initialize the readiness scorer.

        Args:
            min_samples: Minimum samples for reliable training
            max_imbalance_ratio: Maximum acceptable class imbalance ratio
            max_cv_test_gap: Maximum acceptable gap between CV and test scores
            min_acceptable_score: Minimum acceptable model performance
        """
        self.min_samples = min_samples
        self.max_imbalance_ratio = max_imbalance_ratio
        self.max_cv_test_gap = max_cv_test_gap
        self.min_acceptable_score = min_acceptable_score

    def score(
        self,
        n_samples: int,
        n_features: int,
        class_distribution: Optional[Dict[Any, int]] = None,
        missing_ratio: float = 0.0,
        leakage_report: Optional[LeakageReport] = None,
        cv_score: float = 0.0,
        test_score: float = 0.0,
        feature_importance: Optional[Dict[str, float]] = None,
        is_regression: bool = False
    ) -> ReadinessScore:
        """
        Calculate production readiness score.

        Args:
            n_samples: Number of training samples
            n_features: Number of features
            class_distribution: Dict of class -> count (for classification)
            missing_ratio: Proportion of missing values (0-1)
            leakage_report: LeakageReport from leakage detection
            cv_score: Cross-validation score
            test_score: Test set score
            feature_importance: Dict of feature -> importance
            is_regression: Whether this is a regression task

        Returns:
            ReadinessScore with detailed assessment
        """
        components = []
        critical_issues = []
        warnings = []
        recommendations = []

        # 1. Data Quality Score
        data_quality = self._score_data_quality(
            n_samples, n_features, class_distribution, missing_ratio, is_regression
        )
        components.append(data_quality)
        critical_issues.extend([r for r in data_quality.recommendations if 'CRITICAL' in r])
        warnings.extend([r for r in data_quality.recommendations if 'WARNING' in r])

        # 2. Leakage Risk Score
        leakage_score = self._score_leakage_risk(leakage_report)
        components.append(leakage_score)
        critical_issues.extend([r for r in leakage_score.recommendations if 'CRITICAL' in r])
        warnings.extend([r for r in leakage_score.recommendations if 'WARNING' in r])

        # 3. Model Stability Score
        stability_score = self._score_model_stability(cv_score, test_score)
        components.append(stability_score)
        critical_issues.extend([r for r in stability_score.recommendations if 'CRITICAL' in r])
        warnings.extend([r for r in stability_score.recommendations if 'WARNING' in r])

        # 4. Feature Reliability Score
        feature_score = self._score_feature_reliability(feature_importance, leakage_report)
        components.append(feature_score)
        warnings.extend([r for r in feature_score.recommendations if 'WARNING' in r])

        # 5. Performance Score
        perf_score = self._score_performance(test_score, is_regression)
        components.append(perf_score)
        warnings.extend([r for r in perf_score.recommendations if 'WARNING' in r])

        # Calculate weighted overall score
        overall_score = sum(
            c.score * c.weight for c in components
        )

        # Determine readiness level
        readiness_level = self._determine_readiness(
            overall_score, critical_issues, warnings
        )

        # Generate final recommendations
        recommendations = self._generate_recommendations(
            components, critical_issues, warnings, readiness_level
        )

        return ReadinessScore(
            overall_score=round(overall_score, 1),
            readiness_level=readiness_level,
            components=components,
            critical_issues=critical_issues,
            warnings=warnings,
            recommendations=recommendations
        )

    def _score_data_quality(
        self,
        n_samples: int,
        n_features: int,
        class_distribution: Optional[Dict[Any, int]],
        missing_ratio: float,
        is_regression: bool
    ) -> ScoreComponent:
        """Score data quality factors."""
        score = 100.0
        recommendations = []
        details_parts = []

        # Sample size check
        if n_samples < self.min_samples:
            score -= 40
            recommendations.append(
                f"CRITICAL: Only {n_samples} samples. Need at least {self.min_samples} for reliable training."
            )
            details_parts.append(f"Low samples ({n_samples})")
        elif n_samples < self.min_samples * 5:
            score -= 15
            recommendations.append(
                f"WARNING: {n_samples} samples may not be enough for complex models."
            )
            details_parts.append(f"Moderate samples ({n_samples})")
        else:
            details_parts.append(f"Good sample size ({n_samples:,})")

        # Feature ratio check
        if n_samples > 0 and n_features > n_samples / 10:
            score -= 20
            recommendations.append(
                f"WARNING: High feature-to-sample ratio ({n_features}/{n_samples}). Risk of overfitting."
            )
            details_parts.append("High feature ratio")

        # Class imbalance check (classification only)
        if class_distribution and not is_regression:
            counts = list(class_distribution.values())
            if len(counts) >= 2:
                max_count = max(counts)
                min_count = min(counts)
                if min_count > 0:
                    imbalance_ratio = max_count / min_count

                    if imbalance_ratio > self.max_imbalance_ratio * 2:
                        score -= 30
                        recommendations.append(
                            f"CRITICAL: Severe class imbalance ({imbalance_ratio:.1f}:1). "
                            "Consider SMOTE or class weighting."
                        )
                        details_parts.append(f"Severe imbalance ({imbalance_ratio:.1f}:1)")
                    elif imbalance_ratio > self.max_imbalance_ratio:
                        score -= 15
                        recommendations.append(
                            f"WARNING: Class imbalance ({imbalance_ratio:.1f}:1). "
                            "May affect minority class prediction."
                        )
                        details_parts.append(f"Imbalanced ({imbalance_ratio:.1f}:1)")
                    else:
                        details_parts.append("Balanced classes")

        # Missing values check
        if missing_ratio > 0.3:
            score -= 25
            recommendations.append(
                f"CRITICAL: {missing_ratio:.1%} missing values. Data quality is poor."
            )
            details_parts.append(f"High missing ({missing_ratio:.1%})")
        elif missing_ratio > 0.1:
            score -= 10
            recommendations.append(
                f"WARNING: {missing_ratio:.1%} missing values. Imputation may affect results."
            )
            details_parts.append(f"Some missing ({missing_ratio:.1%})")

        score = max(0, score)

        # Determine status
        if score >= 80:
            status = "Good"
        elif score >= 60:
            status = "Acceptable"
        elif score >= 40:
            status = "Needs Attention"
        else:
            status = "Poor"

        return ScoreComponent(
            name="Data Quality",
            score=score,
            weight=self.WEIGHTS['data_quality'],
            status=status,
            details="; ".join(details_parts) if details_parts else "No issues",
            recommendations=recommendations
        )

    def _score_leakage_risk(
        self,
        leakage_report: Optional[LeakageReport]
    ) -> ScoreComponent:
        """Score leakage risk."""
        score = 100.0
        recommendations = []
        details_parts = []

        if leakage_report is None:
            return ScoreComponent(
                name="Leakage Risk",
                score=100.0,
                weight=self.WEIGHTS['leakage_risk'],
                status="Not Checked",
                details="Leakage detection not performed",
                recommendations=["Run leakage detection for production models"]
            )

        # Score based on risk level
        if leakage_report.overall_risk == LeakageRisk.CRITICAL:
            score = 0
            recommendations.append(
                "CRITICAL: Data leakage detected. Model performance is likely overestimated."
            )
            details_parts.append("Critical leakage found")
        elif leakage_report.overall_risk == LeakageRisk.HIGH:
            score = 30
            recommendations.append(
                "CRITICAL: High-risk leakage indicators. Investigate before deployment."
            )
            details_parts.append("High-risk features found")
        elif leakage_report.overall_risk == LeakageRisk.MEDIUM:
            score = 60
            recommendations.append(
                "WARNING: Potential leakage. Review flagged features."
            )
            details_parts.append("Medium-risk features found")
        elif leakage_report.overall_risk == LeakageRisk.LOW:
            score = 90
            details_parts.append("Low risk")

        # Add specific feature warnings
        if leakage_report.high_risk_features:
            details_parts.append(f"Features: {', '.join(leakage_report.high_risk_features[:3])}")

        # Determine status
        if score >= 80:
            status = "Low Risk"
        elif score >= 50:
            status = "Medium Risk"
        else:
            status = "High Risk"

        return ScoreComponent(
            name="Leakage Risk",
            score=score,
            weight=self.WEIGHTS['leakage_risk'],
            status=status,
            details="; ".join(details_parts) if details_parts else "No leakage detected",
            recommendations=recommendations
        )

    def _score_model_stability(
        self,
        cv_score: float,
        test_score: float
    ) -> ScoreComponent:
        """Score model stability (CV vs Test gap)."""
        recommendations = []
        details_parts = []

        if cv_score == 0 and test_score == 0:
            return ScoreComponent(
                name="Model Stability",
                score=50.0,
                weight=self.WEIGHTS['model_stability'],
                status="Unknown",
                details="No scores available",
                recommendations=["Evaluate model on held-out test set"]
            )

        # Calculate gap (CV is usually higher)
        gap = abs(cv_score - test_score)
        relative_gap = gap / max(cv_score, 0.001)

        # Score based on gap
        if relative_gap > self.max_cv_test_gap * 2:
            score = 20
            recommendations.append(
                f"CRITICAL: Large CV-Test gap ({gap:.3f}). Model may not generalize well."
            )
            details_parts.append(f"CV: {cv_score:.3f}, Test: {test_score:.3f}")
            details_parts.append(f"Gap: {gap:.3f} ({relative_gap:.1%})")
        elif relative_gap > self.max_cv_test_gap:
            score = 50
            recommendations.append(
                f"WARNING: Noticeable CV-Test gap ({gap:.3f}). Monitor in production."
            )
            details_parts.append(f"CV: {cv_score:.3f}, Test: {test_score:.3f}")
        elif relative_gap > self.max_cv_test_gap / 2:
            score = 75
            details_parts.append(f"CV: {cv_score:.3f}, Test: {test_score:.3f}")
            details_parts.append("Acceptable gap")
        else:
            score = 95
            details_parts.append(f"CV: {cv_score:.3f}, Test: {test_score:.3f}")
            details_parts.append("Stable performance")

        # Check for test > CV (unusual, might indicate issues)
        if test_score > cv_score * 1.1:
            score = min(score, 60)
            recommendations.append(
                "WARNING: Test score higher than CV. May indicate data leakage or lucky split."
            )

        # Determine status
        if score >= 80:
            status = "Stable"
        elif score >= 50:
            status = "Moderate"
        else:
            status = "Unstable"

        return ScoreComponent(
            name="Model Stability",
            score=score,
            weight=self.WEIGHTS['model_stability'],
            status=status,
            details="; ".join(details_parts),
            recommendations=recommendations
        )

    def _score_feature_reliability(
        self,
        feature_importance: Optional[Dict[str, float]],
        leakage_report: Optional[LeakageReport]
    ) -> ScoreComponent:
        """Score feature reliability."""
        recommendations = []
        details_parts = []

        if not feature_importance:
            return ScoreComponent(
                name="Feature Reliability",
                score=70.0,
                weight=self.WEIGHTS['feature_reliability'],
                status="Unknown",
                details="No feature importance available",
                recommendations=[]
            )

        score = 100.0

        # Check for feature dominance
        sorted_importance = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )

        if sorted_importance:
            total = sum(feature_importance.values())
            if total > 0:
                top_feature, top_importance = sorted_importance[0]
                top_share = top_importance / total

                if top_share > 0.5:
                    score -= 30
                    recommendations.append(
                        f"WARNING: '{top_feature}' dominates predictions ({top_share:.1%}). "
                        "Verify this feature will be available in production."
                    )
                    details_parts.append(f"Dominant: {top_feature} ({top_share:.1%})")
                elif top_share > 0.3:
                    score -= 10
                    details_parts.append(f"Top: {top_feature} ({top_share:.1%})")

                # Check if top feature is flagged for leakage
                if leakage_report and top_feature in leakage_report.high_risk_features:
                    score -= 40
                    recommendations.append(
                        f"CRITICAL: Top feature '{top_feature}' is flagged for leakage risk."
                    )

        # Check feature count
        n_features = len(feature_importance)
        if n_features > 100:
            score -= 10
            recommendations.append(
                "WARNING: High feature count may affect inference latency."
            )
            details_parts.append(f"{n_features} features")

        score = max(0, score)

        # Determine status
        if score >= 80:
            status = "Reliable"
        elif score >= 50:
            status = "Moderate"
        else:
            status = "Concern"

        return ScoreComponent(
            name="Feature Reliability",
            score=score,
            weight=self.WEIGHTS['feature_reliability'],
            status=status,
            details="; ".join(details_parts) if details_parts else "Features look reasonable",
            recommendations=recommendations
        )

    def _score_performance(
        self,
        test_score: float,
        is_regression: bool
    ) -> ScoreComponent:
        """Score model performance."""
        recommendations = []

        if test_score == 0:
            return ScoreComponent(
                name="Performance",
                score=50.0,
                weight=self.WEIGHTS['performance'],
                status="Unknown",
                details="No test score available",
                recommendations=["Evaluate model on test set"]
            )

        # For regression, score might be negative (e.g., neg_rmse)
        # Assume positive scores for now
        score_value = abs(test_score)

        if score_value < self.min_acceptable_score * 0.5:
            score = 20
            recommendations.append(
                f"CRITICAL: Poor model performance ({test_score:.3f}). May not be useful."
            )
            status = "Poor"
        elif score_value < self.min_acceptable_score:
            score = 50
            recommendations.append(
                f"WARNING: Below-target performance ({test_score:.3f}). Consider improving."
            )
            status = "Below Target"
        elif score_value < self.min_acceptable_score + 0.15:
            score = 75
            status = "Acceptable"
        else:
            score = 95
            status = "Good"

        return ScoreComponent(
            name="Performance",
            score=score,
            weight=self.WEIGHTS['performance'],
            status=status,
            details=f"Test score: {test_score:.4f}",
            recommendations=recommendations
        )

    def _determine_readiness(
        self,
        overall_score: float,
        critical_issues: List[str],
        warnings: List[str]
    ) -> ReadinessLevel:
        """Determine overall readiness level."""
        if critical_issues:
            return ReadinessLevel.NOT_READY

        if overall_score >= 80:
            if warnings:
                return ReadinessLevel.READY_WITH_CAUTION
            return ReadinessLevel.READY
        elif overall_score >= 60:
            return ReadinessLevel.READY_WITH_CAUTION
        elif overall_score >= 40:
            return ReadinessLevel.NEEDS_REVIEW
        else:
            return ReadinessLevel.NOT_READY

    def _generate_recommendations(
        self,
        components: List[ScoreComponent],
        critical_issues: List[str],
        warnings: List[str],
        readiness_level: ReadinessLevel
    ) -> List[str]:
        """Generate final recommendations."""
        recommendations = []

        if readiness_level == ReadinessLevel.NOT_READY:
            recommendations.append(
                "Do NOT deploy this model until critical issues are resolved."
            )
        elif readiness_level == ReadinessLevel.NEEDS_REVIEW:
            recommendations.append(
                "Have a data scientist review this model before deployment."
            )
        elif readiness_level == ReadinessLevel.READY_WITH_CAUTION:
            recommendations.append(
                "Deploy with enhanced monitoring for the first few weeks."
            )

        # Add specific action items
        for component in components:
            if component.score < 50:
                recommendations.append(
                    f"Improve {component.name}: {component.details}"
                )

        return recommendations

    def get_summary(self, score: ReadinessScore) -> str:
        """Generate human-readable summary."""
        lines = [
            "=" * 60,
            "PRODUCTION READINESS ASSESSMENT",
            "=" * 60,
            f"Overall Score: {score.overall_score}/100",
            f"Readiness Level: {score.readiness_level.value.upper()}",
            ""
        ]

        # Component scores
        lines.append("Component Scores:")
        lines.append("-" * 40)
        for comp in score.components:
            lines.append(f"  {comp.name}: {comp.score:.0f}/100 ({comp.status})")
            if comp.details:
                lines.append(f"    {comp.details}")

        # Critical issues
        if score.critical_issues:
            lines.append("")
            lines.append("CRITICAL ISSUES:")
            lines.append("-" * 40)
            for issue in score.critical_issues:
                lines.append(f"  ! {issue}")

        # Warnings
        if score.warnings:
            lines.append("")
            lines.append("WARNINGS:")
            lines.append("-" * 40)
            for warning in score.warnings[:5]:  # Limit to 5
                lines.append(f"  - {warning}")

        # Recommendations
        if score.recommendations:
            lines.append("")
            lines.append("RECOMMENDATIONS:")
            lines.append("-" * 40)
            for rec in score.recommendations[:5]:
                lines.append(f"  -> {rec}")

        lines.append("=" * 60)
        return "\n".join(lines)


def assess_readiness(
    n_samples: int,
    n_features: int,
    class_distribution: Optional[Dict[Any, int]] = None,
    missing_ratio: float = 0.0,
    leakage_report: Optional[LeakageReport] = None,
    cv_score: float = 0.0,
    test_score: float = 0.0,
    feature_importance: Optional[Dict[str, float]] = None,
    is_regression: bool = False
) -> ReadinessScore:
    """
    Convenience function to assess production readiness.

    Returns:
        ReadinessScore with detailed assessment
    """
    scorer = ReadinessScorer()
    return scorer.score(
        n_samples=n_samples,
        n_features=n_features,
        class_distribution=class_distribution,
        missing_ratio=missing_ratio,
        leakage_report=leakage_report,
        cv_score=cv_score,
        test_score=test_score,
        feature_importance=feature_importance,
        is_regression=is_regression
    )
