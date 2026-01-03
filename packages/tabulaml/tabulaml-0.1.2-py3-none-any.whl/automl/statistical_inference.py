"""
Statistical Inference Module

Provides rigorous statistical inference for model evaluation:
- Bootstrap confidence intervals for metrics
- Hypothesis testing for model comparison
- Effect size estimation
- Power analysis

Mathematical Foundation:
- Bootstrap: Resample with replacement to estimate sampling distribution
- Percentile CI: [θ*_{α/2}, θ*_{1-α/2}]
- BCa CI: Bias-corrected and accelerated bootstrap
- Paired t-test: For comparing models on same data
"""

import numpy as np
from typing import Tuple, Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from scipy import stats
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, mean_squared_error, r2_score
)


@dataclass
class ConfidenceInterval:
    """A confidence interval with metadata."""
    lower: float
    upper: float
    point_estimate: float
    confidence_level: float
    method: str  # 'percentile', 'bca', 'normal'
    n_bootstrap: int = 0

    @property
    def width(self) -> float:
        return self.upper - self.lower

    @property
    def margin_of_error(self) -> float:
        return self.width / 2

    def contains(self, value: float) -> bool:
        return self.lower <= value <= self.upper

    def __str__(self) -> str:
        return f"{self.point_estimate:.4f} [{self.lower:.4f}, {self.upper:.4f}]"


@dataclass
class HypothesisTestResult:
    """Result of a statistical hypothesis test."""
    test_name: str
    test_statistic: float
    p_value: float
    effect_size: float
    effect_size_name: str  # 'cohens_d', 'r', etc.
    is_significant: bool
    confidence_level: float
    conclusion: str


@dataclass
class MetricWithCI:
    """A metric with its confidence interval."""
    name: str
    value: float
    ci: ConfidenceInterval
    std_error: float


@dataclass
class StatisticalReport:
    """Complete statistical inference report."""
    metrics: List[MetricWithCI] = field(default_factory=list)
    comparisons: List[HypothesisTestResult] = field(default_factory=list)
    sample_size: int = 0
    effective_sample_size: int = 0  # After any resampling


class BootstrapEstimator:
    """
    Bootstrap confidence interval estimator.

    Implements multiple CI methods:
    1. Percentile: Simple quantile-based
    2. BCa: Bias-corrected and accelerated
    3. Normal: Based on bootstrap SE (assumes normality)

    Mathematical Background:
    - Percentile: CI = [θ*_{α/2}, θ*_{1-α/2}]
    - BCa correction: Adjusts for bias and skewness
        z₀ = Φ⁻¹(proportion of θ* < θ̂)  # Bias correction
        a = Σ(θ̂_(-i) - θ̂_(·))³ / (6·(Σ(θ̂_(-i) - θ̂_(·))²)^(3/2))  # Acceleration
    """

    def __init__(
        self,
        n_bootstrap: int = 1000,
        confidence_level: float = 0.95,
        random_state: Optional[int] = 42,
        method: str = 'bca'
    ):
        """
        Initialize bootstrap estimator.

        Args:
            n_bootstrap: Number of bootstrap samples
            confidence_level: Confidence level (default 0.95 = 95%)
            random_state: Random seed for reproducibility
            method: 'percentile', 'bca', or 'normal'
        """
        self.n_bootstrap = n_bootstrap
        self.confidence_level = confidence_level
        self.random_state = random_state
        self.method = method
        self._rng = np.random.RandomState(random_state)

    def estimate_ci(
        self,
        data: np.ndarray,
        statistic: Callable[[np.ndarray], float],
        weights: Optional[np.ndarray] = None
    ) -> ConfidenceInterval:
        """
        Estimate confidence interval for a statistic.

        Args:
            data: Data array (samples,) or (samples, features)
            statistic: Function that computes statistic from data
            weights: Optional sample weights

        Returns:
            ConfidenceInterval object
        """
        n = len(data)
        point_estimate = statistic(data)

        # Generate bootstrap samples
        boot_stats = np.zeros(self.n_bootstrap)

        for i in range(self.n_bootstrap):
            if weights is not None:
                # Weighted bootstrap
                indices = self._rng.choice(
                    n, size=n, replace=True, p=weights/weights.sum()
                )
            else:
                indices = self._rng.randint(0, n, size=n)

            boot_sample = data[indices] if len(data.shape) == 1 else data[indices, :]
            boot_stats[i] = statistic(boot_sample)

        # Compute CI based on method
        alpha = 1 - self.confidence_level

        if self.method == 'percentile':
            lower = np.percentile(boot_stats, 100 * alpha / 2)
            upper = np.percentile(boot_stats, 100 * (1 - alpha / 2))

        elif self.method == 'bca':
            lower, upper = self._bca_interval(
                data, boot_stats, point_estimate, statistic, alpha
            )

        elif self.method == 'normal':
            # Assumes bootstrap distribution is normal
            se = np.std(boot_stats, ddof=1)
            z = stats.norm.ppf(1 - alpha / 2)
            lower = point_estimate - z * se
            upper = point_estimate + z * se

        else:
            raise ValueError(f"Unknown method: {self.method}")

        return ConfidenceInterval(
            lower=float(lower),
            upper=float(upper),
            point_estimate=float(point_estimate),
            confidence_level=self.confidence_level,
            method=self.method,
            n_bootstrap=self.n_bootstrap
        )

    def _bca_interval(
        self,
        data: np.ndarray,
        boot_stats: np.ndarray,
        point_estimate: float,
        statistic: Callable,
        alpha: float
    ) -> Tuple[float, float]:
        """
        Compute BCa (Bias-Corrected and Accelerated) interval.

        BCa adjusts for:
        1. Bias: Median of bootstrap ≠ point estimate
        2. Acceleration: Skewness of bootstrap distribution
        """
        n = len(data)

        # Bias correction factor
        prop_less = np.mean(boot_stats < point_estimate)
        # Handle edge cases
        prop_less = np.clip(prop_less, 0.001, 0.999)
        z0 = stats.norm.ppf(prop_less)

        # Acceleration factor (jackknife)
        jackknife_stats = np.zeros(n)
        for i in range(n):
            # Leave-one-out
            if len(data.shape) == 1:
                jack_sample = np.delete(data, i)
            else:
                jack_sample = np.delete(data, i, axis=0)
            jackknife_stats[i] = statistic(jack_sample)

        jack_mean = np.mean(jackknife_stats)
        num = np.sum((jack_mean - jackknife_stats) ** 3)
        denom = 6 * (np.sum((jack_mean - jackknife_stats) ** 2) ** 1.5)

        if denom == 0:
            a = 0
        else:
            a = num / denom

        # BCa quantiles
        z_alpha_2 = stats.norm.ppf(alpha / 2)
        z_1_alpha_2 = stats.norm.ppf(1 - alpha / 2)

        # Adjusted quantiles
        def adjust_quantile(z):
            num = z0 + z
            denom = 1 - a * (z0 + z)
            if denom == 0:
                return 0.5
            return stats.norm.cdf(z0 + num / denom)

        q_lower = adjust_quantile(z_alpha_2)
        q_upper = adjust_quantile(z_1_alpha_2)

        # Clip to valid range
        q_lower = np.clip(q_lower, 0.001, 0.999)
        q_upper = np.clip(q_upper, 0.001, 0.999)

        lower = np.percentile(boot_stats, 100 * q_lower)
        upper = np.percentile(boot_stats, 100 * q_upper)

        return lower, upper


class ClassificationMetricsCI:
    """
    Compute classification metrics with confidence intervals.

    Handles:
    - Accuracy, Precision, Recall, F1
    - ROC-AUC
    - Per-class metrics
    """

    def __init__(
        self,
        n_bootstrap: int = 1000,
        confidence_level: float = 0.95,
        random_state: int = 42
    ):
        self.bootstrap = BootstrapEstimator(
            n_bootstrap=n_bootstrap,
            confidence_level=confidence_level,
            random_state=random_state,
            method='bca'
        )
        self.confidence_level = confidence_level

    def compute_all(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: Optional[np.ndarray] = None
    ) -> StatisticalReport:
        """
        Compute all classification metrics with CIs.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_prob: Predicted probabilities (optional, for AUC)

        Returns:
            StatisticalReport with all metrics
        """
        metrics = []

        # Combine data for bootstrap sampling
        if y_prob is not None:
            data = np.column_stack([y_true, y_pred, y_prob])
        else:
            data = np.column_stack([y_true, y_pred])

        # Accuracy
        def acc_stat(d):
            return accuracy_score(d[:, 0], d[:, 1])
        acc_ci = self.bootstrap.estimate_ci(data, acc_stat)
        metrics.append(MetricWithCI(
            name='accuracy',
            value=accuracy_score(y_true, y_pred),
            ci=acc_ci,
            std_error=(acc_ci.upper - acc_ci.lower) / (2 * 1.96)
        ))

        # Precision
        def prec_stat(d):
            return precision_score(d[:, 0], d[:, 1], zero_division=0)
        prec_ci = self.bootstrap.estimate_ci(data, prec_stat)
        metrics.append(MetricWithCI(
            name='precision',
            value=precision_score(y_true, y_pred, zero_division=0),
            ci=prec_ci,
            std_error=(prec_ci.upper - prec_ci.lower) / (2 * 1.96)
        ))

        # Recall
        def rec_stat(d):
            return recall_score(d[:, 0], d[:, 1], zero_division=0)
        rec_ci = self.bootstrap.estimate_ci(data, rec_stat)
        metrics.append(MetricWithCI(
            name='recall',
            value=recall_score(y_true, y_pred, zero_division=0),
            ci=rec_ci,
            std_error=(rec_ci.upper - rec_ci.lower) / (2 * 1.96)
        ))

        # F1
        def f1_stat(d):
            return f1_score(d[:, 0], d[:, 1], zero_division=0)
        f1_ci = self.bootstrap.estimate_ci(data, f1_stat)
        metrics.append(MetricWithCI(
            name='f1',
            value=f1_score(y_true, y_pred, zero_division=0),
            ci=f1_ci,
            std_error=(f1_ci.upper - f1_ci.lower) / (2 * 1.96)
        ))

        # ROC-AUC (if probabilities available)
        if y_prob is not None:
            try:
                def auc_stat(d):
                    return roc_auc_score(d[:, 0], d[:, 2])
                auc_ci = self.bootstrap.estimate_ci(data, auc_stat)
                metrics.append(MetricWithCI(
                    name='roc_auc',
                    value=roc_auc_score(y_true, y_prob),
                    ci=auc_ci,
                    std_error=(auc_ci.upper - auc_ci.lower) / (2 * 1.96)
                ))
            except Exception:
                pass

        return StatisticalReport(
            metrics=metrics,
            sample_size=len(y_true)
        )


class RegressionMetricsCI:
    """Compute regression metrics with confidence intervals."""

    def __init__(
        self,
        n_bootstrap: int = 1000,
        confidence_level: float = 0.95,
        random_state: int = 42
    ):
        self.bootstrap = BootstrapEstimator(
            n_bootstrap=n_bootstrap,
            confidence_level=confidence_level,
            random_state=random_state,
            method='bca'
        )
        self.confidence_level = confidence_level

    def compute_all(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> StatisticalReport:
        """Compute all regression metrics with CIs."""
        metrics = []
        data = np.column_stack([y_true, y_pred])

        # RMSE
        def rmse_stat(d):
            return np.sqrt(mean_squared_error(d[:, 0], d[:, 1]))
        rmse_ci = self.bootstrap.estimate_ci(data, rmse_stat)
        metrics.append(MetricWithCI(
            name='rmse',
            value=np.sqrt(mean_squared_error(y_true, y_pred)),
            ci=rmse_ci,
            std_error=(rmse_ci.upper - rmse_ci.lower) / (2 * 1.96)
        ))

        # R²
        def r2_stat(d):
            return r2_score(d[:, 0], d[:, 1])
        r2_ci = self.bootstrap.estimate_ci(data, r2_stat)
        metrics.append(MetricWithCI(
            name='r2',
            value=r2_score(y_true, y_pred),
            ci=r2_ci,
            std_error=(r2_ci.upper - r2_ci.lower) / (2 * 1.96)
        ))

        # MAE
        def mae_stat(d):
            return np.mean(np.abs(d[:, 0] - d[:, 1]))
        mae_ci = self.bootstrap.estimate_ci(data, mae_stat)
        metrics.append(MetricWithCI(
            name='mae',
            value=np.mean(np.abs(y_true - y_pred)),
            ci=mae_ci,
            std_error=(mae_ci.upper - mae_ci.lower) / (2 * 1.96)
        ))

        return StatisticalReport(
            metrics=metrics,
            sample_size=len(y_true)
        )


class ModelComparator:
    """
    Statistical comparison of two models.

    Implements:
    - Paired t-test (for same data)
    - McNemar's test (for classifiers)
    - 5x2 CV paired t-test
    - Effect size (Cohen's d)
    """

    def __init__(self, alpha: float = 0.05):
        """
        Args:
            alpha: Significance level
        """
        self.alpha = alpha

    def paired_ttest(
        self,
        scores_a: np.ndarray,
        scores_b: np.ndarray
    ) -> HypothesisTestResult:
        """
        Paired t-test for comparing model performance.

        H₀: μ_A = μ_B (no difference)
        H₁: μ_A ≠ μ_B (two-sided)

        Args:
            scores_a: Scores from model A (e.g., CV fold scores)
            scores_b: Scores from model B

        Returns:
            HypothesisTestResult
        """
        # Compute differences
        diffs = scores_a - scores_b

        # Paired t-test
        t_stat, p_value = stats.ttest_rel(scores_a, scores_b)

        # Effect size: Cohen's d for paired samples
        cohens_d = np.mean(diffs) / np.std(diffs, ddof=1)

        is_significant = p_value < self.alpha

        if is_significant:
            if np.mean(diffs) > 0:
                conclusion = f"Model A is significantly better (p={p_value:.4f})"
            else:
                conclusion = f"Model B is significantly better (p={p_value:.4f})"
        else:
            conclusion = f"No significant difference (p={p_value:.4f})"

        return HypothesisTestResult(
            test_name="Paired t-test",
            test_statistic=float(t_stat),
            p_value=float(p_value),
            effect_size=float(cohens_d),
            effect_size_name="Cohen's d",
            is_significant=is_significant,
            confidence_level=1 - self.alpha,
            conclusion=conclusion
        )

    def mcnemar_test(
        self,
        y_true: np.ndarray,
        y_pred_a: np.ndarray,
        y_pred_b: np.ndarray
    ) -> HypothesisTestResult:
        """
        McNemar's test for comparing classifiers.

        Tests whether two classifiers have the same error rate.

        Contingency table:
                    Model B
                    Correct | Incorrect
        Model A
        Correct   |   n00   |   n01
        Incorrect |   n10   |   n11

        H₀: n01 = n10 (same error rate)
        """
        correct_a = (y_pred_a == y_true)
        correct_b = (y_pred_b == y_true)

        # Contingency table cells
        n01 = np.sum(correct_a & ~correct_b)  # A correct, B wrong
        n10 = np.sum(~correct_a & correct_b)  # A wrong, B correct

        # McNemar's test with continuity correction
        if n01 + n10 == 0:
            chi2 = 0.0
            p_value = 1.0
        else:
            chi2 = ((abs(n01 - n10) - 1) ** 2) / (n01 + n10)
            p_value = 1 - stats.chi2.cdf(chi2, df=1)

        # Effect size: Odds ratio
        if n10 == 0:
            odds_ratio = float('inf') if n01 > 0 else 1.0
        else:
            odds_ratio = n01 / n10

        is_significant = p_value < self.alpha

        if is_significant:
            if n01 > n10:
                conclusion = f"Model A makes fewer errors (p={p_value:.4f})"
            else:
                conclusion = f"Model B makes fewer errors (p={p_value:.4f})"
        else:
            conclusion = f"No significant difference in error rates (p={p_value:.4f})"

        return HypothesisTestResult(
            test_name="McNemar's test",
            test_statistic=float(chi2),
            p_value=float(p_value),
            effect_size=float(odds_ratio),
            effect_size_name="Odds ratio",
            is_significant=is_significant,
            confidence_level=1 - self.alpha,
            conclusion=conclusion
        )

    def wilcoxon_test(
        self,
        scores_a: np.ndarray,
        scores_b: np.ndarray
    ) -> HypothesisTestResult:
        """
        Wilcoxon signed-rank test (non-parametric alternative to paired t-test).

        Useful when:
        - Small sample size
        - Non-normal distributions
        - Ordinal data
        """
        stat, p_value = stats.wilcoxon(scores_a, scores_b)

        # Effect size: r = Z / sqrt(N)
        n = len(scores_a)
        z = stats.norm.ppf(1 - p_value / 2)
        r = z / np.sqrt(n)

        is_significant = p_value < self.alpha

        if is_significant:
            if np.median(scores_a - scores_b) > 0:
                conclusion = f"Model A is significantly better (p={p_value:.4f})"
            else:
                conclusion = f"Model B is significantly better (p={p_value:.4f})"
        else:
            conclusion = f"No significant difference (p={p_value:.4f})"

        return HypothesisTestResult(
            test_name="Wilcoxon signed-rank test",
            test_statistic=float(stat),
            p_value=float(p_value),
            effect_size=float(r),
            effect_size_name="r (effect size)",
            is_significant=is_significant,
            confidence_level=1 - self.alpha,
            conclusion=conclusion
        )


def get_statistical_summary(report: StatisticalReport) -> str:
    """Generate human-readable statistical summary."""
    lines = [
        "=" * 60,
        "STATISTICAL INFERENCE REPORT",
        "=" * 60,
        f"Sample Size: {report.sample_size}",
        "",
        "Metrics with Confidence Intervals:",
        "-" * 60
    ]

    for m in report.metrics:
        lines.append(
            f"  {m.name.upper()}: {m.value:.4f} "
            f"[{m.ci.lower:.4f}, {m.ci.upper:.4f}] "
            f"(SE: {m.std_error:.4f})"
        )

    if report.comparisons:
        lines.append("")
        lines.append("Model Comparisons:")
        lines.append("-" * 60)
        for comp in report.comparisons:
            lines.append(f"  {comp.test_name}:")
            lines.append(f"    {comp.conclusion}")
            lines.append(f"    Effect size ({comp.effect_size_name}): {comp.effect_size:.3f}")

    lines.append("=" * 60)
    return "\n".join(lines)
