"""
Data Drift Detection Module

Monitors for distribution shift between training and production data.

Types of Drift:
1. Covariate Drift: P(X) changes but P(Y|X) stays same
2. Prior Drift: P(Y) changes
3. Concept Drift: P(Y|X) changes

Statistical Tests:
- KS Test: Kolmogorov-Smirnov for continuous features
- Chi-Square: For categorical features
- PSI: Population Stability Index
- JS Divergence: Jensen-Shannon for distribution comparison
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from scipy import stats
from scipy.spatial.distance import jensenshannon


class DriftSeverity(Enum):
    """Severity levels for drift detection."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class DriftType(Enum):
    """Types of data drift."""
    COVARIATE = "covariate"  # P(X) changes
    PRIOR = "prior"          # P(Y) changes
    CONCEPT = "concept"      # P(Y|X) changes


@dataclass
class FeatureDrift:
    """Drift analysis for a single feature."""
    feature_name: str
    drift_score: float  # PSI or KS statistic
    p_value: Optional[float]
    severity: DriftSeverity
    test_used: str  # 'ks', 'chi2', 'psi'
    reference_stats: Dict[str, float] = field(default_factory=dict)
    current_stats: Dict[str, float] = field(default_factory=dict)
    is_drifted: bool = False


@dataclass
class DriftReport:
    """Complete drift analysis report."""
    overall_drift_score: float
    overall_severity: DriftSeverity
    drifted_features: List[str] = field(default_factory=list)
    feature_drifts: List[FeatureDrift] = field(default_factory=list)
    reference_size: int = 0
    current_size: int = 0
    n_features: int = 0
    timestamp: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)

    @property
    def drift_percentage(self) -> float:
        """Percentage of features that have drifted."""
        if not self.feature_drifts:
            return 0.0
        return 100 * len(self.drifted_features) / len(self.feature_drifts)


# Alias for backward compatibility
FeatureDriftResult = FeatureDrift


class PSICalculator:
    """
    Population Stability Index (PSI) Calculator.

    PSI measures the shift in distribution of a feature between two populations.

    Formula:
        PSI = Σᵢ (Actualᵢ - Expectedᵢ) × ln(Actualᵢ / Expectedᵢ)

    where i indexes the bins.

    Interpretation:
        PSI < 0.1: No significant shift
        0.1 ≤ PSI < 0.2: Moderate shift
        PSI ≥ 0.2: Significant shift - action required
    """

    def __init__(self, n_bins: int = 10, min_bin_size: float = 0.001):
        """
        Args:
            n_bins: Number of bins for discretization
            min_bin_size: Minimum bin proportion to avoid log(0)
        """
        self.n_bins = n_bins
        self.min_bin_size = min_bin_size

    def calculate(
        self,
        reference: np.ndarray,
        current: np.ndarray,
        bins: Optional[np.ndarray] = None
    ) -> Tuple[float, np.ndarray]:
        """
        Calculate PSI between reference and current distributions.

        Args:
            reference: Reference (training) distribution
            current: Current (production) distribution
            bins: Pre-computed bin edges (optional)

        Returns:
            (psi_value, bin_edges)
        """
        # Create bins from reference distribution
        if bins is None:
            # Use quantiles for more robust binning
            percentiles = np.linspace(0, 100, self.n_bins + 1)
            bins = np.percentile(reference, percentiles)
            bins = np.unique(bins)  # Remove duplicates

        # Handle edge cases
        bins[0] = -np.inf
        bins[-1] = np.inf

        # Compute proportions in each bin
        ref_counts, _ = np.histogram(reference, bins=bins)
        cur_counts, _ = np.histogram(current, bins=bins)

        ref_props = ref_counts / len(reference)
        cur_props = cur_counts / len(current)

        # Apply minimum to avoid log(0)
        ref_props = np.maximum(ref_props, self.min_bin_size)
        cur_props = np.maximum(cur_props, self.min_bin_size)

        # Renormalize
        ref_props = ref_props / ref_props.sum()
        cur_props = cur_props / cur_props.sum()

        # Calculate PSI
        psi = np.sum((cur_props - ref_props) * np.log(cur_props / ref_props))

        return float(psi), bins

    @staticmethod
    def interpret_psi(psi: float) -> DriftSeverity:
        """Interpret PSI value as drift severity."""
        if psi < 0.1:
            return DriftSeverity.NONE
        elif psi < 0.2:
            return DriftSeverity.LOW
        elif psi < 0.25:
            return DriftSeverity.MODERATE
        elif psi < 0.5:
            return DriftSeverity.HIGH
        else:
            return DriftSeverity.CRITICAL


class DriftDetector:
    """
    Production-grade drift detector.

    Monitors multiple aspects of data drift:
    1. Feature-level drift (covariate)
    2. Label drift (prior)
    3. Prediction drift (potential concept drift)
    """

    def __init__(
        self,
        psi_threshold: float = 0.2,
        ks_threshold: float = 0.1,
        p_value_threshold: float = 0.05,
        n_bins: int = 10
    ):
        """
        Initialize drift detector.

        Args:
            psi_threshold: PSI threshold for declaring drift
            ks_threshold: KS statistic threshold
            p_value_threshold: P-value threshold for statistical tests
            n_bins: Number of bins for PSI calculation
        """
        self.psi_threshold = psi_threshold
        self.ks_threshold = ks_threshold
        self.p_value_threshold = p_value_threshold
        self.n_bins = n_bins
        self.psi_calc = PSICalculator(n_bins=n_bins)

        # Store reference distributions
        self._reference_data: Optional[pd.DataFrame] = None
        self._reference_stats: Dict[str, Dict] = {}
        self._bin_edges: Dict[str, np.ndarray] = {}

    def fit_reference(
        self,
        data: Union[pd.DataFrame, np.ndarray],
        feature_names: Optional[List[str]] = None
    ) -> 'DriftDetector':
        """
        Fit detector to reference (training) data.

        Args:
            data: Reference dataset
            feature_names: Names of features (if data is ndarray)
        """
        if isinstance(data, np.ndarray):
            if feature_names is None:
                feature_names = [f"feature_{i}" for i in range(data.shape[1])]
            data = pd.DataFrame(data, columns=feature_names)

        self._reference_data = data.copy()

        # Compute reference statistics for each feature
        for col in data.columns:
            self._reference_stats[col] = self._compute_stats(data[col])

            # Pre-compute bins for continuous features
            if data[col].dtype in [np.float64, np.float32, np.int64, np.int32]:
                _, bins = self.psi_calc.calculate(
                    data[col].dropna().values,
                    data[col].dropna().values
                )
                self._bin_edges[col] = bins

        return self

    def compute_baseline(
        self,
        data: Union[pd.DataFrame, np.ndarray],
        feature_names: Optional[List[str]] = None
    ) -> DriftReport:
        """
        Compute and store baseline statistics for drift monitoring.

        This is a convenience method that fits the reference and returns
        a baseline report that can be saved for production monitoring.

        Args:
            data: Reference (training) data
            feature_names: Names of features (if data is ndarray)

        Returns:
            DriftReport with baseline statistics (no drift detected)
        """
        # Fit reference data
        self.fit_reference(data, feature_names)

        # Convert to DataFrame if needed
        if isinstance(data, np.ndarray):
            if feature_names is None:
                feature_names = [f"feature_{i}" for i in range(data.shape[1])]
            data = pd.DataFrame(data, columns=feature_names)

        # Create baseline report (self-comparison = no drift)
        return DriftReport(
            overall_drift_score=0.0,
            overall_severity=DriftSeverity.NONE,
            drifted_features=[],
            feature_drifts=[],
            reference_size=len(data),
            current_size=0,
            n_features=len(data.columns) if hasattr(data, 'columns') else data.shape[1],
            recommendations=["Baseline established. Use detect() to monitor for drift."]
        )

    def detect(
        self,
        current_data: Union[pd.DataFrame, np.ndarray],
        feature_names: Optional[List[str]] = None
    ) -> DriftReport:
        """
        Detect drift between reference and current data.

        Args:
            current_data: New/production data to check
            feature_names: Names of features (if data is ndarray)

        Returns:
            DriftReport with detailed drift analysis
        """
        if self._reference_data is None:
            raise ValueError("Must call fit_reference() first")

        if isinstance(current_data, np.ndarray):
            if feature_names is None:
                feature_names = list(self._reference_data.columns)
            current_data = pd.DataFrame(current_data, columns=feature_names)

        feature_drifts = []
        drifted_features = []

        # Check each feature
        for col in self._reference_data.columns:
            if col not in current_data.columns:
                continue

            ref_values = self._reference_data[col].dropna().values
            cur_values = current_data[col].dropna().values

            if len(cur_values) == 0:
                continue

            # Detect drift based on feature type
            if self._is_categorical(self._reference_data[col]):
                drift = self._detect_categorical_drift(col, ref_values, cur_values)
            else:
                drift = self._detect_numerical_drift(col, ref_values, cur_values)

            feature_drifts.append(drift)

            if drift.is_drifted:
                drifted_features.append(col)

        # Compute overall drift score
        if feature_drifts:
            overall_score = np.mean([fd.drift_score for fd in feature_drifts])
            psi_scores = [fd.drift_score for fd in feature_drifts if fd.test_used == 'psi']
            if psi_scores:
                overall_severity = self._compute_overall_severity(psi_scores)
            else:
                overall_severity = self._compute_overall_severity(
                    [fd.drift_score for fd in feature_drifts]
                )
        else:
            overall_score = 0.0
            overall_severity = DriftSeverity.NONE

        # Generate recommendations
        recommendations = self._generate_recommendations(
            drifted_features, feature_drifts, overall_severity
        )

        return DriftReport(
            overall_drift_score=overall_score,
            overall_severity=overall_severity,
            drifted_features=drifted_features,
            feature_drifts=feature_drifts,
            reference_size=len(self._reference_data),
            current_size=len(current_data),
            n_features=len(feature_drifts),
            recommendations=recommendations
        )

    def _detect_numerical_drift(
        self,
        col: str,
        reference: np.ndarray,
        current: np.ndarray
    ) -> FeatureDrift:
        """Detect drift in numerical feature using KS test and PSI."""
        # Kolmogorov-Smirnov test
        ks_stat, ks_pvalue = stats.ks_2samp(reference, current)

        # PSI
        bins = self._bin_edges.get(col)
        psi_score, _ = self.psi_calc.calculate(reference, current, bins)

        # Use PSI as primary score, but consider both
        is_drifted = (
            psi_score >= self.psi_threshold or
            (ks_stat >= self.ks_threshold and ks_pvalue < self.p_value_threshold)
        )

        severity = self.psi_calc.interpret_psi(psi_score)

        return FeatureDrift(
            feature_name=col,
            drift_score=psi_score,
            p_value=ks_pvalue,
            severity=severity,
            test_used='psi',
            reference_stats=self._reference_stats.get(col, {}),
            current_stats=self._compute_stats(pd.Series(current)),
            is_drifted=is_drifted
        )

    def _detect_categorical_drift(
        self,
        col: str,
        reference: np.ndarray,
        current: np.ndarray
    ) -> FeatureDrift:
        """Detect drift in categorical feature using Chi-square test."""
        # Get all unique categories
        all_categories = np.union1d(reference, current)

        # Count frequencies
        ref_counts = np.array([np.sum(reference == cat) for cat in all_categories])
        cur_counts = np.array([np.sum(current == cat) for cat in all_categories])

        # Normalize to proportions
        ref_props = ref_counts / len(reference)
        cur_props = cur_counts / len(current)

        # Chi-square test
        # Use expected frequencies based on reference distribution
        expected = ref_props * len(current)
        expected = np.maximum(expected, 1)  # Avoid divide by zero

        try:
            chi2_stat, p_value = stats.chisquare(cur_counts, f_exp=expected)
        except Exception:
            chi2_stat, p_value = 0.0, 1.0

        # Also compute PSI-like metric for categories
        eps = 1e-10
        ref_props_adj = np.maximum(ref_props, eps)
        cur_props_adj = np.maximum(cur_props, eps)
        psi_like = np.sum((cur_props_adj - ref_props_adj) *
                         np.log(cur_props_adj / ref_props_adj))

        is_drifted = p_value < self.p_value_threshold

        if psi_like < 0.1:
            severity = DriftSeverity.NONE
        elif psi_like < 0.2:
            severity = DriftSeverity.LOW
        elif psi_like < 0.3:
            severity = DriftSeverity.MODERATE
        else:
            severity = DriftSeverity.HIGH

        return FeatureDrift(
            feature_name=col,
            drift_score=psi_like,
            p_value=p_value,
            severity=severity,
            test_used='chi2',
            reference_stats={'n_categories': len(all_categories)},
            current_stats={'n_categories': len(np.unique(current))},
            is_drifted=is_drifted
        )

    def _compute_stats(self, series: pd.Series) -> Dict[str, float]:
        """Compute summary statistics for a feature."""
        if self._is_categorical(series):
            return {
                'n_unique': series.nunique(),
                'mode': str(series.mode().iloc[0]) if len(series.mode()) > 0 else None,
                'missing_rate': series.isna().mean()
            }
        else:
            return {
                'mean': float(series.mean()),
                'std': float(series.std()),
                'min': float(series.min()),
                'max': float(series.max()),
                'median': float(series.median()),
                'q25': float(series.quantile(0.25)),
                'q75': float(series.quantile(0.75)),
                'missing_rate': float(series.isna().mean())
            }

    @staticmethod
    def _is_categorical(series: pd.Series) -> bool:
        """Check if a series is categorical."""
        if series.dtype == 'object' or series.dtype.name == 'category':
            return True
        if series.dtype in [np.int64, np.int32]:
            # Check if it looks like a categorical
            return series.nunique() < 20
        return False

    def _compute_overall_severity(
        self,
        scores: List[float]
    ) -> DriftSeverity:
        """Compute overall drift severity from individual scores."""
        mean_score = np.mean(scores)
        max_score = np.max(scores)
        pct_drifted = np.mean([s >= self.psi_threshold for s in scores])

        if max_score >= 0.5 or pct_drifted >= 0.5:
            return DriftSeverity.CRITICAL
        elif max_score >= 0.25 or pct_drifted >= 0.3:
            return DriftSeverity.HIGH
        elif mean_score >= 0.15:
            return DriftSeverity.MODERATE
        elif mean_score >= 0.1:
            return DriftSeverity.LOW
        else:
            return DriftSeverity.NONE

    def _generate_recommendations(
        self,
        drifted_features: List[str],
        feature_drifts: List[FeatureDrift],
        severity: DriftSeverity
    ) -> List[str]:
        """Generate actionable recommendations based on drift analysis."""
        recommendations = []

        if severity == DriftSeverity.CRITICAL:
            recommendations.append(
                "CRITICAL: Significant data drift detected. "
                "Model retraining is strongly recommended."
            )
        elif severity == DriftSeverity.HIGH:
            recommendations.append(
                "HIGH DRIFT: Consider retraining the model or "
                "implementing online learning."
            )
        elif severity == DriftSeverity.MODERATE:
            recommendations.append(
                "MODERATE DRIFT: Monitor model performance closely. "
                "Schedule retraining if performance degrades."
            )

        if drifted_features:
            if len(drifted_features) <= 5:
                recommendations.append(
                    f"Features with significant drift: {', '.join(drifted_features)}"
                )
            else:
                recommendations.append(
                    f"{len(drifted_features)} features show significant drift. "
                    "Review feature engineering pipeline."
                )

            # Check for high-importance drifted features
            high_drift = [fd for fd in feature_drifts
                         if fd.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]]
            if high_drift:
                recommendations.append(
                    f"High-severity drift in: "
                    f"{', '.join([fd.feature_name for fd in high_drift[:3]])}"
                )

        return recommendations

    def get_summary(self, report: DriftReport) -> str:
        """Generate human-readable drift summary."""
        lines = [
            "=" * 60,
            "DATA DRIFT ANALYSIS REPORT",
            "=" * 60,
            f"Reference Size: {report.reference_size:,}",
            f"Current Size: {report.current_size:,}",
            f"Overall Drift Score: {report.overall_drift_score:.4f}",
            f"Overall Severity: {report.overall_severity.value.upper()}",
            f"Features Drifted: {len(report.drifted_features)}/{len(report.feature_drifts)} "
            f"({report.drift_percentage:.1f}%)",
            ""
        ]

        if report.drifted_features:
            lines.append("Drifted Features:")
            lines.append("-" * 40)
            for fd in report.feature_drifts:
                if fd.is_drifted:
                    lines.append(
                        f"  {fd.feature_name}: PSI={fd.drift_score:.4f} "
                        f"({fd.severity.value})"
                    )

        if report.recommendations:
            lines.append("")
            lines.append("Recommendations:")
            lines.append("-" * 40)
            for rec in report.recommendations:
                lines.append(f"  - {rec}")

        lines.append("=" * 60)
        return "\n".join(lines)


class ConceptDriftDetector:
    """
    Detects concept drift using prediction monitoring.

    Monitors:
    1. Prediction distribution shift
    2. Confidence distribution shift
    3. Error rate changes (if labels available)
    """

    def __init__(self, window_size: int = 1000):
        """
        Args:
            window_size: Size of sliding window for detection
        """
        self.window_size = window_size
        self._reference_predictions: Optional[np.ndarray] = None
        self._reference_confidences: Optional[np.ndarray] = None

    def fit_reference(
        self,
        predictions: np.ndarray,
        confidences: Optional[np.ndarray] = None
    ) -> 'ConceptDriftDetector':
        """Store reference predictions from training/validation."""
        self._reference_predictions = predictions.copy()
        if confidences is not None:
            self._reference_confidences = confidences.copy()
        return self

    def detect(
        self,
        predictions: np.ndarray,
        confidences: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Detect potential concept drift from predictions.

        Returns:
            Dict with drift metrics and alerts
        """
        if self._reference_predictions is None:
            raise ValueError("Must call fit_reference() first")

        results = {}

        # Check prediction distribution shift
        psi_calc = PSICalculator()

        if np.issubdtype(predictions.dtype, np.integer):
            # Classification: check class distribution shift
            ref_class_dist = np.bincount(self._reference_predictions) / len(self._reference_predictions)
            cur_class_dist = np.bincount(predictions, minlength=len(ref_class_dist)) / len(predictions)

            # Jensen-Shannon divergence
            js_div = jensenshannon(ref_class_dist, cur_class_dist)
            results['prediction_js_divergence'] = float(js_div)
            results['prediction_drift'] = js_div > 0.1
        else:
            # Regression: check prediction value distribution
            psi, _ = psi_calc.calculate(self._reference_predictions, predictions)
            results['prediction_psi'] = float(psi)
            results['prediction_drift'] = psi > 0.2

        # Check confidence distribution shift
        if confidences is not None and self._reference_confidences is not None:
            conf_psi, _ = psi_calc.calculate(self._reference_confidences, confidences)
            results['confidence_psi'] = float(conf_psi)
            results['confidence_drift'] = conf_psi > 0.15

            # Low confidence rate
            low_conf_threshold = np.percentile(self._reference_confidences, 10)
            ref_low_conf_rate = np.mean(self._reference_confidences < low_conf_threshold)
            cur_low_conf_rate = np.mean(confidences < low_conf_threshold)
            results['low_confidence_rate_change'] = cur_low_conf_rate - ref_low_conf_rate

        results['needs_attention'] = (
            results.get('prediction_drift', False) or
            results.get('confidence_drift', False)
        )

        return results
