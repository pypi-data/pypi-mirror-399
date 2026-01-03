"""
Prediction Uncertainty Quantification Module

Provides rigorous uncertainty estimates for model predictions using:
1. Conformal Prediction - Distribution-free prediction intervals with coverage guarantees
2. Ensemble Disagreement - Variance across ensemble members
3. Monte Carlo Dropout - Bayesian approximation via dropout at inference
4. Quantile Regression - Direct prediction interval estimation

Mathematical Foundation:
- Conformal prediction provides valid coverage P(Y ∈ C(X)) ≥ 1-α for any distribution
- Ensemble variance σ² = (1/M) Σ(f_m(x) - f̄(x))² measures epistemic uncertainty
- Aleatoric uncertainty captured through prediction spread
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Union
from enum import Enum
import warnings


class UncertaintyType(Enum):
    """Types of uncertainty in predictions."""
    EPISTEMIC = "epistemic"  # Model uncertainty (reducible with more data)
    ALEATORIC = "aleatoric"  # Data uncertainty (irreducible noise)
    TOTAL = "total"          # Combined uncertainty


@dataclass
class PredictionInterval:
    """Prediction interval with uncertainty quantification."""
    lower: float
    upper: float
    point_estimate: float
    confidence_level: float
    uncertainty_type: UncertaintyType = UncertaintyType.TOTAL

    @property
    def width(self) -> float:
        """Interval width - narrower is better for same coverage."""
        return self.upper - self.lower

    @property
    def relative_uncertainty(self) -> float:
        """Relative uncertainty as fraction of point estimate."""
        if abs(self.point_estimate) < 1e-10:
            return float('inf')
        return self.width / (2 * abs(self.point_estimate))

    def contains(self, value: float) -> bool:
        """Check if value falls within interval."""
        return self.lower <= value <= self.upper


@dataclass
class ClassificationUncertainty:
    """Uncertainty metrics for classification predictions."""
    predicted_class: int
    predicted_proba: np.ndarray
    entropy: float              # Shannon entropy of predictions
    max_proba: float           # Maximum class probability
    margin: float              # Difference between top 2 probabilities
    epistemic_uncertainty: float = 0.0
    aleatoric_uncertainty: float = 0.0

    @property
    def is_confident(self) -> bool:
        """Whether prediction is confident (low uncertainty)."""
        return self.max_proba > 0.8 and self.margin > 0.3

    @property
    def uncertainty_score(self) -> float:
        """Overall uncertainty score [0, 1], higher = more uncertain."""
        # Combine entropy and margin into single score
        normalized_entropy = self.entropy / np.log(len(self.predicted_proba))
        margin_uncertainty = 1 - self.margin
        return 0.5 * normalized_entropy + 0.5 * margin_uncertainty


@dataclass
class UncertaintyReport:
    """Complete uncertainty analysis report."""
    method: str
    coverage_level: float
    intervals: List[PredictionInterval] = field(default_factory=list)
    classification_uncertainties: List[ClassificationUncertainty] = field(default_factory=list)
    mean_interval_width: float = 0.0
    empirical_coverage: Optional[float] = None
    calibration_error: Optional[float] = None

    def get_high_uncertainty_indices(self, threshold: float = 0.5) -> np.ndarray:
        """Get indices of predictions with high uncertainty."""
        if self.classification_uncertainties:
            scores = [u.uncertainty_score for u in self.classification_uncertainties]
            return np.where(np.array(scores) > threshold)[0]
        elif self.intervals:
            # For regression, use relative uncertainty
            scores = [i.relative_uncertainty for i in self.intervals]
            median_width = np.median(scores)
            return np.where(np.array(scores) > 2 * median_width)[0]
        return np.array([])


class ConformalPredictor:
    """
    Conformal Prediction for distribution-free uncertainty quantification.

    Provides prediction sets/intervals with guaranteed coverage:
    P(Y ∈ C(X)) ≥ 1 - α for any data distribution.

    Methods:
    - Split Conformal: Simple, uses held-out calibration set
    - CV+ Conformal: Better efficiency, uses cross-validation
    """

    def __init__(self, confidence_level: float = 0.9):
        """
        Initialize conformal predictor.

        Args:
            confidence_level: Target coverage probability (1 - α)
        """
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
        self.calibration_scores = None
        self.quantile = None
        self.is_fitted = False

    def _compute_nonconformity_scores(
        self,
        model,
        X: np.ndarray,
        y: np.ndarray,
        task_type: str = "regression"
    ) -> np.ndarray:
        """
        Compute nonconformity scores measuring prediction error.

        For regression: |y - ŷ|
        For classification: 1 - p(y_true)
        """
        if task_type == "regression":
            predictions = model.predict(X)
            return np.abs(y - predictions)
        else:
            # Classification: probability of true class
            probas = model.predict_proba(X)
            true_class_proba = probas[np.arange(len(y)), y.astype(int)]
            return 1 - true_class_proba

    def calibrate(
        self,
        model,
        X_calib: np.ndarray,
        y_calib: np.ndarray,
        task_type: str = "regression"
    ) -> None:
        """
        Calibrate conformal predictor using held-out calibration data.

        Args:
            model: Fitted model
            X_calib: Calibration features
            y_calib: Calibration targets
            task_type: 'regression' or 'classification'
        """
        self.calibration_scores = self._compute_nonconformity_scores(
            model, X_calib, y_calib, task_type
        )

        # Compute quantile with finite-sample correction
        n = len(self.calibration_scores)
        # Quantile level for finite sample coverage guarantee
        adjusted_quantile = np.ceil((n + 1) * self.confidence_level) / n
        adjusted_quantile = min(adjusted_quantile, 1.0)

        self.quantile = np.quantile(self.calibration_scores, adjusted_quantile)
        self.is_fitted = True
        self.task_type = task_type

    def predict_interval(
        self,
        model,
        X: np.ndarray
    ) -> List[PredictionInterval]:
        """
        Generate prediction intervals for regression.

        Returns intervals [ŷ - q, ŷ + q] where q is calibrated quantile.
        """
        if not self.is_fitted:
            raise ValueError("Must call calibrate() before predict_interval()")

        predictions = model.predict(X)
        intervals = []

        for pred in predictions:
            intervals.append(PredictionInterval(
                lower=pred - self.quantile,
                upper=pred + self.quantile,
                point_estimate=pred,
                confidence_level=self.confidence_level,
                uncertainty_type=UncertaintyType.TOTAL
            ))

        return intervals

    def predict_set(
        self,
        model,
        X: np.ndarray,
        class_labels: Optional[np.ndarray] = None
    ) -> List[List[int]]:
        """
        Generate prediction sets for classification.

        Returns sets of classes with total probability ≥ 1 - α.
        """
        if not self.is_fitted:
            raise ValueError("Must call calibrate() before predict_set()")

        probas = model.predict_proba(X)
        prediction_sets = []

        for proba in probas:
            # Include classes until cumulative probability exceeds threshold
            sorted_indices = np.argsort(proba)[::-1]
            cumsum = 0
            pred_set = []

            for idx in sorted_indices:
                pred_set.append(idx)
                cumsum += proba[idx]
                # Include class if its nonconformity score is below quantile
                if 1 - cumsum <= self.quantile:
                    break

            prediction_sets.append(pred_set)

        return prediction_sets


class EnsembleUncertainty:
    """
    Uncertainty estimation via ensemble disagreement.

    Uses variance across ensemble members to estimate epistemic uncertainty:
    - High variance → model is uncertain (different members disagree)
    - Low variance → model is confident (members agree)

    For classification, also decomposes into:
    - Epistemic: Mutual information I(y; θ|x, D)
    - Aleatoric: Expected entropy E[H(y|x, θ)]
    """

    def __init__(self):
        self.ensemble_models = []

    def set_ensemble(self, models: List[Any]) -> None:
        """Set ensemble of models for uncertainty estimation."""
        self.ensemble_models = models

    def estimate_regression_uncertainty(
        self,
        X: np.ndarray,
        confidence_level: float = 0.9
    ) -> List[PredictionInterval]:
        """
        Estimate prediction intervals from ensemble variance.

        Interval: ŷ ± z_{α/2} * σ where σ is ensemble standard deviation.
        """
        if not self.ensemble_models:
            raise ValueError("Must set ensemble models first")

        # Get predictions from all ensemble members
        all_predictions = np.array([
            model.predict(X) for model in self.ensemble_models
        ])

        mean_pred = np.mean(all_predictions, axis=0)
        std_pred = np.std(all_predictions, axis=0)

        # Z-score for confidence level (assuming approximate normality)
        from scipy import stats
        z_score = stats.norm.ppf((1 + confidence_level) / 2)

        intervals = []
        for i in range(len(X)):
            intervals.append(PredictionInterval(
                lower=mean_pred[i] - z_score * std_pred[i],
                upper=mean_pred[i] + z_score * std_pred[i],
                point_estimate=mean_pred[i],
                confidence_level=confidence_level,
                uncertainty_type=UncertaintyType.EPISTEMIC
            ))

        return intervals

    def estimate_classification_uncertainty(
        self,
        X: np.ndarray
    ) -> List[ClassificationUncertainty]:
        """
        Estimate classification uncertainty with epistemic/aleatoric decomposition.

        Uses information-theoretic decomposition:
        - Total: H(E[p(y|x)])  - entropy of mean prediction
        - Aleatoric: E[H(p(y|x))] - mean entropy across ensemble
        - Epistemic: Total - Aleatoric = mutual information
        """
        if not self.ensemble_models:
            raise ValueError("Must set ensemble models first")

        # Get probability predictions from all ensemble members
        all_probas = np.array([
            model.predict_proba(X) for model in self.ensemble_models
        ])  # Shape: (n_models, n_samples, n_classes)

        # Mean probability across ensemble
        mean_proba = np.mean(all_probas, axis=0)  # (n_samples, n_classes)

        uncertainties = []
        for i in range(len(X)):
            proba = mean_proba[i]

            # Total uncertainty: entropy of mean prediction
            total_entropy = -np.sum(proba * np.log(proba + 1e-10))

            # Aleatoric: mean entropy across ensemble members
            member_entropies = []
            for m in range(len(self.ensemble_models)):
                p = all_probas[m, i]
                h = -np.sum(p * np.log(p + 1e-10))
                member_entropies.append(h)
            aleatoric = np.mean(member_entropies)

            # Epistemic: mutual information (total - aleatoric)
            epistemic = max(0, total_entropy - aleatoric)

            # Other metrics
            max_proba = np.max(proba)
            sorted_proba = np.sort(proba)[::-1]
            margin = sorted_proba[0] - sorted_proba[1] if len(sorted_proba) > 1 else 1.0

            uncertainties.append(ClassificationUncertainty(
                predicted_class=int(np.argmax(proba)),
                predicted_proba=proba,
                entropy=total_entropy,
                max_proba=max_proba,
                margin=margin,
                epistemic_uncertainty=epistemic,
                aleatoric_uncertainty=aleatoric
            ))

        return uncertainties


class QuantileRegressor:
    """
    Quantile Regression for direct prediction interval estimation.

    Trains separate models for different quantiles to estimate
    conditional quantiles Q_τ(Y|X) directly.

    For interval [α/2, 1-α/2], provides prediction intervals with
    approximate coverage 1-α.
    """

    def __init__(self, confidence_level: float = 0.9):
        self.confidence_level = confidence_level
        self.lower_quantile = (1 - confidence_level) / 2
        self.upper_quantile = 1 - self.lower_quantile
        self.lower_model = None
        self.upper_model = None
        self.median_model = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Fit quantile regression models.

        Uses gradient boosting with quantile loss for flexibility.
        """
        try:
            from sklearn.ensemble import GradientBoostingRegressor
        except ImportError:
            raise ImportError("scikit-learn required for quantile regression")

        # Lower quantile model
        self.lower_model = GradientBoostingRegressor(
            loss='quantile',
            alpha=self.lower_quantile,
            n_estimators=100,
            max_depth=3,
            random_state=42
        )
        self.lower_model.fit(X, y)

        # Median model (point estimate)
        self.median_model = GradientBoostingRegressor(
            loss='quantile',
            alpha=0.5,
            n_estimators=100,
            max_depth=3,
            random_state=42
        )
        self.median_model.fit(X, y)

        # Upper quantile model
        self.upper_model = GradientBoostingRegressor(
            loss='quantile',
            alpha=self.upper_quantile,
            n_estimators=100,
            max_depth=3,
            random_state=42
        )
        self.upper_model.fit(X, y)

    def predict_interval(self, X: np.ndarray) -> List[PredictionInterval]:
        """Generate prediction intervals using quantile predictions."""
        if self.lower_model is None:
            raise ValueError("Must fit models first")

        lower_pred = self.lower_model.predict(X)
        median_pred = self.median_model.predict(X)
        upper_pred = self.upper_model.predict(X)

        intervals = []
        for i in range(len(X)):
            # Ensure lower < upper (quantile crossing correction)
            lo, hi = lower_pred[i], upper_pred[i]
            if lo > hi:
                lo, hi = hi, lo

            intervals.append(PredictionInterval(
                lower=lo,
                upper=hi,
                point_estimate=median_pred[i],
                confidence_level=self.confidence_level,
                uncertainty_type=UncertaintyType.ALEATORIC
            ))

        return intervals


class UncertaintyQuantifier:
    """
    Main interface for prediction uncertainty quantification.

    Combines multiple methods to provide robust uncertainty estimates:
    1. Conformal prediction for coverage guarantees
    2. Ensemble methods for epistemic uncertainty
    3. Entropy-based metrics for classification confidence
    """

    def __init__(
        self,
        confidence_level: float = 0.9,
        method: str = "conformal"
    ):
        """
        Initialize uncertainty quantifier.

        Args:
            confidence_level: Target coverage/confidence (default 90%)
            method: 'conformal', 'ensemble', 'quantile', or 'auto'
        """
        self.confidence_level = confidence_level
        self.method = method

        self.conformal = ConformalPredictor(confidence_level)
        self.ensemble_uncertainty = EnsembleUncertainty()
        self.quantile_regressor = QuantileRegressor(confidence_level)

        self.is_calibrated = False
        self.task_type = None

    def calibrate(
        self,
        model,
        X_calib: np.ndarray,
        y_calib: np.ndarray,
        task_type: str = "regression",
        ensemble_models: Optional[List] = None
    ) -> None:
        """
        Calibrate uncertainty quantifier.

        Args:
            model: Primary fitted model
            X_calib: Calibration features (held-out data)
            y_calib: Calibration targets
            task_type: 'regression' or 'classification'
            ensemble_models: List of ensemble members (optional)
        """
        self.task_type = task_type

        # Calibrate conformal predictor
        self.conformal.calibrate(model, X_calib, y_calib, task_type)

        # Set up ensemble if provided
        if ensemble_models:
            self.ensemble_uncertainty.set_ensemble(ensemble_models)

        # Fit quantile regressor for regression tasks
        if task_type == "regression" and self.method in ["quantile", "auto"]:
            try:
                self.quantile_regressor.fit(X_calib, y_calib)
            except Exception as e:
                warnings.warn(f"Quantile regression fitting failed: {e}")

        self.is_calibrated = True

    def quantify(
        self,
        model,
        X: np.ndarray,
        y_true: Optional[np.ndarray] = None
    ) -> UncertaintyReport:
        """
        Quantify prediction uncertainty.

        Args:
            model: Fitted model
            X: Features to predict
            y_true: True values (optional, for coverage evaluation)

        Returns:
            UncertaintyReport with intervals/uncertainties
        """
        if not self.is_calibrated:
            raise ValueError("Must call calibrate() first")

        report = UncertaintyReport(
            method=self.method,
            coverage_level=self.confidence_level
        )

        if self.task_type == "regression":
            report = self._quantify_regression(model, X, y_true, report)
        else:
            report = self._quantify_classification(model, X, y_true, report)

        return report

    def _quantify_regression(
        self,
        model,
        X: np.ndarray,
        y_true: Optional[np.ndarray],
        report: UncertaintyReport
    ) -> UncertaintyReport:
        """Quantify regression uncertainty."""

        # Primary method: conformal prediction
        if self.method in ["conformal", "auto"]:
            intervals = self.conformal.predict_interval(model, X)
            report.intervals = intervals
            report.mean_interval_width = np.mean([i.width for i in intervals])

        # Ensemble uncertainty if available
        if self.ensemble_uncertainty.ensemble_models:
            ensemble_intervals = self.ensemble_uncertainty.estimate_regression_uncertainty(
                X, self.confidence_level
            )
            # Combine with conformal intervals
            if report.intervals:
                for i, (conf_int, ens_int) in enumerate(zip(report.intervals, ensemble_intervals)):
                    # Average the bounds
                    report.intervals[i] = PredictionInterval(
                        lower=(conf_int.lower + ens_int.lower) / 2,
                        upper=(conf_int.upper + ens_int.upper) / 2,
                        point_estimate=conf_int.point_estimate,
                        confidence_level=self.confidence_level,
                        uncertainty_type=UncertaintyType.TOTAL
                    )
            else:
                report.intervals = ensemble_intervals

        # Evaluate coverage if true values provided
        if y_true is not None and report.intervals:
            covered = sum(
                interval.contains(y)
                for interval, y in zip(report.intervals, y_true)
            )
            report.empirical_coverage = covered / len(y_true)
            report.calibration_error = abs(
                report.empirical_coverage - self.confidence_level
            )

        return report

    def _quantify_classification(
        self,
        model,
        X: np.ndarray,
        y_true: Optional[np.ndarray],
        report: UncertaintyReport
    ) -> UncertaintyReport:
        """Quantify classification uncertainty."""

        # Get probability predictions
        probas = model.predict_proba(X)

        uncertainties = []
        for i, proba in enumerate(probas):
            # Shannon entropy
            entropy = -np.sum(proba * np.log(proba + 1e-10))

            # Confidence metrics
            max_proba = np.max(proba)
            sorted_proba = np.sort(proba)[::-1]
            margin = sorted_proba[0] - sorted_proba[1] if len(sorted_proba) > 1 else 1.0

            uncertainties.append(ClassificationUncertainty(
                predicted_class=int(np.argmax(proba)),
                predicted_proba=proba,
                entropy=entropy,
                max_proba=max_proba,
                margin=margin
            ))

        # Add ensemble uncertainty decomposition if available
        if self.ensemble_uncertainty.ensemble_models:
            ensemble_uncertainties = self.ensemble_uncertainty.estimate_classification_uncertainty(X)
            for i, ens_u in enumerate(ensemble_uncertainties):
                uncertainties[i].epistemic_uncertainty = ens_u.epistemic_uncertainty
                uncertainties[i].aleatoric_uncertainty = ens_u.aleatoric_uncertainty

        report.classification_uncertainties = uncertainties

        # Get prediction sets from conformal
        if self.method in ["conformal", "auto"]:
            prediction_sets = self.conformal.predict_set(model, X)
            # Could add prediction sets to report if needed

        return report

    def get_uncertain_predictions(
        self,
        report: UncertaintyReport,
        threshold: float = 0.5
    ) -> np.ndarray:
        """
        Identify predictions with high uncertainty.

        Args:
            report: Uncertainty report from quantify()
            threshold: Uncertainty threshold (0-1 scale)

        Returns:
            Indices of high-uncertainty predictions
        """
        return report.get_high_uncertainty_indices(threshold)


def compute_prediction_entropy(probas: np.ndarray) -> np.ndarray:
    """
    Compute Shannon entropy of probability predictions.

    H(p) = -Σ p_i * log(p_i)

    Higher entropy = more uncertainty.
    """
    # Handle edge cases
    probas = np.clip(probas, 1e-10, 1.0)
    entropy = -np.sum(probas * np.log(probas), axis=-1)
    return entropy


def compute_prediction_margin(probas: np.ndarray) -> np.ndarray:
    """
    Compute margin between top two class probabilities.

    Higher margin = more confident prediction.
    """
    sorted_probas = np.sort(probas, axis=-1)[:, ::-1]
    if sorted_probas.shape[1] < 2:
        return np.ones(len(probas))
    return sorted_probas[:, 0] - sorted_probas[:, 1]


def expected_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10
) -> float:
    """
    Compute Expected Calibration Error (ECE).

    ECE = Σ (n_b / N) * |acc(b) - conf(b)|

    Measures how well predicted probabilities match actual outcomes.
    """
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0

    for i in range(n_bins):
        in_bin = (y_prob > bin_boundaries[i]) & (y_prob <= bin_boundaries[i + 1])
        prop_in_bin = np.mean(in_bin)

        if prop_in_bin > 0:
            avg_confidence = np.mean(y_prob[in_bin])
            avg_accuracy = np.mean(y_true[in_bin])
            ece += prop_in_bin * np.abs(avg_accuracy - avg_confidence)

    return ece
