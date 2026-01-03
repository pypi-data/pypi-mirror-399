"""
Leakage Detection Module

Detects potential data leakage issues:
- Post-event features (e.g., 'duration' in call data)
- Target leakage (features derived from target)
- Suspiciously high correlations
- Known problematic feature patterns
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class LeakageRisk(Enum):
    """Risk levels for potential leakage."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class LeakageWarning:
    """A single leakage warning."""
    feature: str
    risk_level: LeakageRisk
    reason: str
    recommendation: str
    importance_rank: Optional[int] = None
    correlation_with_target: Optional[float] = None


@dataclass
class LeakageReport:
    """Full leakage analysis report."""
    warnings: List[LeakageWarning] = field(default_factory=list)
    high_risk_features: List[str] = field(default_factory=list)
    overall_risk: LeakageRisk = LeakageRisk.LOW
    recommendations: List[str] = field(default_factory=list)

    @property
    def has_critical_issues(self) -> bool:
        return any(w.risk_level == LeakageRisk.CRITICAL for w in self.warnings)

    @property
    def has_high_risk(self) -> bool:
        return any(w.risk_level in [LeakageRisk.HIGH, LeakageRisk.CRITICAL]
                   for w in self.warnings)

    @property
    def medium_risk_features(self) -> List[str]:
        """Get list of MEDIUM risk features."""
        return [
            w.feature for w in self.warnings
            if w.risk_level == LeakageRisk.MEDIUM
        ]

    @property
    def all_risky_features(self) -> List[str]:
        """Get all features with MEDIUM, HIGH, or CRITICAL risk (recommended to drop)."""
        return [
            w.feature for w in self.warnings
            if w.risk_level in [LeakageRisk.MEDIUM, LeakageRisk.HIGH, LeakageRisk.CRITICAL]
        ]


# Known problematic feature patterns by domain
KNOWN_LEAKAGE_PATTERNS = {
    # Bank Marketing / Call Center datasets
    'duration': {
        'risk': LeakageRisk.CRITICAL,
        'reason': "Call duration is only known AFTER the call ends. Cannot be used to predict who to call.",
        'recommendation': "Remove 'duration' from features or use it only for post-hoc analysis."
    },
    'call_duration': {
        'risk': LeakageRisk.CRITICAL,
        'reason': "Call duration is post-event data - not available at prediction time.",
        'recommendation': "Remove this feature for production models."
    },

    # Transaction / Event timestamps
    'transaction_time': {
        'risk': LeakageRisk.HIGH,
        'reason': "Transaction timestamp may leak information about outcome.",
        'recommendation': "Verify this feature is available at prediction time."
    },
    'event_timestamp': {
        'risk': LeakageRisk.MEDIUM,
        'reason': "Event timestamps can leak temporal information.",
        'recommendation': "Consider if this timestamp is known before the prediction is needed."
    },

    # Outcome-derived features
    'outcome': {
        'risk': LeakageRisk.CRITICAL,
        'reason': "Feature named 'outcome' may be derived from target.",
        'recommendation': "Verify this is not a variant of the target variable."
    },
    'result': {
        'risk': LeakageRisk.HIGH,
        'reason': "Feature named 'result' may contain target information.",
        'recommendation': "Check if this feature is available before the outcome is known."
    },
    'success': {
        'risk': LeakageRisk.HIGH,
        'reason': "Feature named 'success' may be related to target.",
        'recommendation': "Verify independence from target variable."
    },

    # ID-like features that may encode target
    'customer_segment': {
        'risk': LeakageRisk.MEDIUM,
        'reason': "Customer segments may be post-hoc classifications.",
        'recommendation': "Verify segment was assigned before the outcome."
    },
}

# Patterns that suggest post-event data
POST_EVENT_PATTERNS = [
    'duration', 'elapsed', 'total_time', 'time_spent',
    'final_', 'end_', 'outcome_', 'result_',
    '_after', '_post', '_final', '_total',
    'completed_', 'finished_'
]

# Patterns suggesting ID or identifier (usually not leakage but not useful)
ID_PATTERNS = [
    '_id', 'id_', 'uuid', 'guid', 'identifier',
    'row_num', 'index', 'record_'
]


class LeakageDetector:
    """
    Detects potential data leakage in features.

    Leakage occurs when:
    1. Features contain information not available at prediction time
    2. Features are derived from the target variable
    3. Features have suspiciously high correlation with target
    """

    def __init__(
        self,
        correlation_threshold: float = 0.95,
        importance_threshold: float = 0.5,
        check_known_patterns: bool = True
    ):
        """
        Initialize the leakage detector.

        Args:
            correlation_threshold: Flag features with correlation > this value
            importance_threshold: Flag if top feature has > this importance share
            check_known_patterns: Check against known problematic patterns
        """
        self.correlation_threshold = correlation_threshold
        self.importance_threshold = importance_threshold
        self.check_known_patterns = check_known_patterns

    def detect(
        self,
        df: pd.DataFrame,
        target_column: str,
        feature_importance: Optional[Dict[str, float]] = None
    ) -> LeakageReport:
        """
        Analyze dataset for potential leakage.

        Args:
            df: DataFrame with features and target
            target_column: Name of target column
            feature_importance: Optional dict of feature -> importance scores

        Returns:
            LeakageReport with all warnings and recommendations
        """
        report = LeakageReport()
        feature_columns = [c for c in df.columns if c != target_column]

        # 1. Check known problematic patterns
        if self.check_known_patterns:
            self._check_known_patterns(feature_columns, report)

        # 2. Check for post-event naming patterns
        self._check_post_event_patterns(feature_columns, report)

        # 3. Check correlations with target
        self._check_correlations(df, target_column, feature_columns, report)

        # 4. Check feature importance concentration
        if feature_importance:
            self._check_importance_concentration(feature_importance, report)

        # 5. Check for ID-like columns (not leakage but warning)
        self._check_id_columns(feature_columns, report)

        # Compile high-risk features
        report.high_risk_features = [
            w.feature for w in report.warnings
            if w.risk_level in [LeakageRisk.HIGH, LeakageRisk.CRITICAL]
        ]

        # Set overall risk
        if any(w.risk_level == LeakageRisk.CRITICAL for w in report.warnings):
            report.overall_risk = LeakageRisk.CRITICAL
        elif any(w.risk_level == LeakageRisk.HIGH for w in report.warnings):
            report.overall_risk = LeakageRisk.HIGH
        elif any(w.risk_level == LeakageRisk.MEDIUM for w in report.warnings):
            report.overall_risk = LeakageRisk.MEDIUM

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)

        return report

    def _check_known_patterns(
        self,
        features: List[str],
        report: LeakageReport
    ):
        """Check features against known leakage patterns."""
        for feature in features:
            feature_lower = feature.lower()

            # Direct match
            if feature_lower in KNOWN_LEAKAGE_PATTERNS:
                pattern = KNOWN_LEAKAGE_PATTERNS[feature_lower]
                report.warnings.append(LeakageWarning(
                    feature=feature,
                    risk_level=pattern['risk'],
                    reason=pattern['reason'],
                    recommendation=pattern['recommendation']
                ))
            else:
                # Partial match
                for pattern_name, pattern_info in KNOWN_LEAKAGE_PATTERNS.items():
                    if pattern_name in feature_lower:
                        report.warnings.append(LeakageWarning(
                            feature=feature,
                            risk_level=LeakageRisk.MEDIUM,
                            reason=f"Feature name contains '{pattern_name}' - {pattern_info['reason']}",
                            recommendation=pattern_info['recommendation']
                        ))
                        break

    def _check_post_event_patterns(
        self,
        features: List[str],
        report: LeakageReport
    ):
        """Check for naming patterns suggesting post-event data."""
        already_flagged = {w.feature for w in report.warnings}

        for feature in features:
            if feature in already_flagged:
                continue

            feature_lower = feature.lower()

            for pattern in POST_EVENT_PATTERNS:
                if pattern in feature_lower:
                    report.warnings.append(LeakageWarning(
                        feature=feature,
                        risk_level=LeakageRisk.MEDIUM,
                        reason=f"Feature name suggests post-event data (contains '{pattern}')",
                        recommendation="Verify this feature is available at prediction time."
                    ))
                    break

    def _check_correlations(
        self,
        df: pd.DataFrame,
        target_column: str,
        features: List[str],
        report: LeakageReport
    ):
        """Check for suspiciously high correlations with target."""
        already_flagged = {w.feature for w in report.warnings}

        try:
            # Only check numeric columns
            numeric_features = df[features].select_dtypes(include=[np.number]).columns

            if len(numeric_features) == 0:
                return

            # Calculate correlations
            target_series = df[target_column]
            if not np.issubdtype(target_series.dtype, np.number):
                # Encode categorical target for correlation
                target_series = pd.factorize(target_series)[0]

            for feature in numeric_features:
                if feature in already_flagged:
                    continue

                try:
                    corr = abs(df[feature].corr(pd.Series(target_series)))

                    if corr >= self.correlation_threshold:
                        report.warnings.append(LeakageWarning(
                            feature=feature,
                            risk_level=LeakageRisk.CRITICAL,
                            reason=f"Extremely high correlation with target ({corr:.3f})",
                            recommendation="This feature may be derived from target or contain target leakage.",
                            correlation_with_target=corr
                        ))
                    elif corr >= 0.8:
                        report.warnings.append(LeakageWarning(
                            feature=feature,
                            risk_level=LeakageRisk.HIGH,
                            reason=f"Very high correlation with target ({corr:.3f})",
                            recommendation="Investigate if this correlation is legitimate.",
                            correlation_with_target=corr
                        ))
                except Exception:
                    pass  # Skip features that can't be correlated

        except Exception:
            pass  # Skip correlation check if it fails

    def _check_importance_concentration(
        self,
        feature_importance: Dict[str, float],
        report: LeakageReport
    ):
        """Check if one feature dominates importance."""
        if not feature_importance:
            return

        # Sort by importance
        sorted_importance = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )

        if not sorted_importance:
            return

        top_feature, top_importance = sorted_importance[0]
        total_importance = sum(feature_importance.values())

        if total_importance > 0:
            importance_share = top_importance / total_importance

            if importance_share >= self.importance_threshold:
                # Check if already flagged
                already_flagged = {w.feature for w in report.warnings}

                if top_feature not in already_flagged:
                    report.warnings.append(LeakageWarning(
                        feature=top_feature,
                        risk_level=LeakageRisk.HIGH,
                        reason=f"Single feature dominates importance ({importance_share:.1%} of total)",
                        recommendation="Verify this feature doesn't contain leakage.",
                        importance_rank=1
                    ))
                else:
                    # Update existing warning with importance info
                    for w in report.warnings:
                        if w.feature == top_feature:
                            w.importance_rank = 1
                            if w.risk_level == LeakageRisk.MEDIUM:
                                w.risk_level = LeakageRisk.HIGH
                            w.reason += f" AND dominates feature importance ({importance_share:.1%})"

    def _check_id_columns(
        self,
        features: List[str],
        report: LeakageReport
    ):
        """Check for ID-like columns (not useful for prediction)."""
        already_flagged = {w.feature for w in report.warnings}

        for feature in features:
            if feature in already_flagged:
                continue

            feature_lower = feature.lower()

            for pattern in ID_PATTERNS:
                if pattern in feature_lower:
                    report.warnings.append(LeakageWarning(
                        feature=feature,
                        risk_level=LeakageRisk.LOW,
                        reason="Appears to be an ID column (not useful for prediction)",
                        recommendation="Consider removing ID columns from features."
                    ))
                    break

    def _generate_recommendations(self, report: LeakageReport) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        critical_features = [
            w.feature for w in report.warnings
            if w.risk_level == LeakageRisk.CRITICAL
        ]
        high_features = [
            w.feature for w in report.warnings
            if w.risk_level == LeakageRisk.HIGH
        ]

        if critical_features:
            recommendations.append(
                f"CRITICAL: Remove or investigate these features before deployment: "
                f"{', '.join(critical_features)}"
            )

        if high_features:
            recommendations.append(
                f"HIGH RISK: Verify these features are available at prediction time: "
                f"{', '.join(high_features)}"
            )

        if report.has_critical_issues:
            recommendations.append(
                "Model performance may be artificially inflated due to data leakage."
            )
            recommendations.append(
                "Retrain the model after removing problematic features to get realistic estimates."
            )

        return recommendations

    def get_summary(self, report: LeakageReport) -> str:
        """Generate human-readable summary."""
        lines = [
            "=" * 60,
            "LEAKAGE DETECTION REPORT",
            "=" * 60,
            f"Overall Risk Level: {report.overall_risk.value.upper()}",
            f"Total Warnings: {len(report.warnings)}",
            ""
        ]

        if report.warnings:
            # Group by risk level
            by_risk = {}
            for w in report.warnings:
                if w.risk_level not in by_risk:
                    by_risk[w.risk_level] = []
                by_risk[w.risk_level].append(w)

            for risk_level in [LeakageRisk.CRITICAL, LeakageRisk.HIGH,
                              LeakageRisk.MEDIUM, LeakageRisk.LOW]:
                if risk_level in by_risk:
                    lines.append(f"\n{risk_level.value.upper()} RISK:")
                    lines.append("-" * 40)
                    for w in by_risk[risk_level]:
                        lines.append(f"  Feature: {w.feature}")
                        lines.append(f"    {w.reason}")
                        lines.append(f"    -> {w.recommendation}")
        else:
            lines.append("No leakage issues detected.")

        if report.recommendations:
            lines.append("\n" + "=" * 60)
            lines.append("RECOMMENDATIONS:")
            for rec in report.recommendations:
                lines.append(f"  - {rec}")

        lines.append("=" * 60)
        return "\n".join(lines)


def detect_leakage(
    df: pd.DataFrame,
    target_column: str,
    feature_importance: Optional[Dict[str, float]] = None
) -> LeakageReport:
    """
    Convenience function to detect leakage.

    Args:
        df: DataFrame with features and target
        target_column: Name of target column
        feature_importance: Optional feature importance dict

    Returns:
        LeakageReport with analysis results
    """
    detector = LeakageDetector()
    return detector.detect(df, target_column, feature_importance)
