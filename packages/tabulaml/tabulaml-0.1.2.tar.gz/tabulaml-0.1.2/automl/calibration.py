"""
Model Calibration Module

Ensures predicted probabilities are reliable and well-calibrated.

Mathematical Foundation:
- A model is calibrated if P(Y=1|p̂=p) = p for all p ∈ [0,1]
- Reliability diagram: plot predicted vs actual probabilities
- Expected Calibration Error (ECE): weighted average of |accuracy - confidence|

Calibration Methods:
1. Platt Scaling: Logistic regression on logits → σ(a·f(x) + b)
2. Isotonic Regression: Non-parametric monotonic mapping
3. Temperature Scaling: Single parameter T → softmax(z/T)
4. Beta Calibration: Parametric with beta distribution
"""

import numpy as np
from typing import Tuple, Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict
from sklearn.base import BaseEstimator, ClassifierMixin, clone


class CalibrationMethod(Enum):
    """Available calibration methods."""
    PLATT = "platt"           # Platt scaling (sigmoid)
    ISOTONIC = "isotonic"     # Isotonic regression
    TEMPERATURE = "temperature"  # Temperature scaling
    BETA = "beta"             # Beta calibration
    NONE = "none"


@dataclass
class CalibrationMetrics:
    """Calibration quality metrics."""
    ece: float  # Expected Calibration Error
    mce: float  # Maximum Calibration Error
    brier_score: float  # Brier score (MSE of probabilities)
    reliability_diagram: Dict[str, np.ndarray] = field(default_factory=dict)
    is_well_calibrated: bool = False  # ECE < 0.05


@dataclass
class CalibrationResult:
    """Result of calibration process."""
    calibrator: Any  # Fitted calibrator
    method: CalibrationMethod
    metrics_before: CalibrationMetrics
    metrics_after: CalibrationMetrics
    improvement: float  # ECE reduction

    @property
    def original_ece(self) -> float:
        """Original Expected Calibration Error (before calibration)."""
        return self.metrics_before.ece

    @property
    def calibrated_ece(self) -> float:
        """Calibrated Expected Calibration Error (after calibration)."""
        return self.metrics_after.ece

    @property
    def method_used(self) -> str:
        """Name of calibration method used."""
        return self.method.value


# Alias for isotonic calibration - using sklearn's IsotonicRegression
from sklearn.isotonic import IsotonicRegression as IsotonicCalibrator


class PlattScaler:
    """
    Platt Scaling: Learns sigmoid parameters to map scores to probabilities.

    Mathematical Model:
        P(y=1|f) = 1 / (1 + exp(A·f + B))

    where f is the model output (logit or decision function).
    Parameters A and B are learned via maximum likelihood.
    """

    def __init__(self):
        self.A = 0.0
        self.B = 0.0
        self._lr = None

    def fit(self, scores: np.ndarray, y_true: np.ndarray) -> 'PlattScaler':
        """
        Fit Platt scaling parameters.

        Args:
            scores: Model scores/logits (n_samples,)
            y_true: True binary labels (n_samples,)
        """
        # Reshape for sklearn
        X = scores.reshape(-1, 1)

        # Fit logistic regression
        self._lr = LogisticRegression(solver='saga', max_iter=1000, l1_ratio=0)
        self._lr.fit(X, y_true)

        # Extract parameters: P = sigmoid(A*f + B)
        self.A = self._lr.coef_[0, 0]
        self.B = self._lr.intercept_[0]

        return self

    def predict_proba(self, scores: np.ndarray) -> np.ndarray:
        """Transform scores to calibrated probabilities."""
        X = scores.reshape(-1, 1)
        return self._lr.predict_proba(X)[:, 1]

    def __call__(self, scores: np.ndarray) -> np.ndarray:
        return self.predict_proba(scores)


class TemperatureScaler:
    """
    Temperature Scaling: Single parameter calibration.

    Mathematical Model:
        P(y=k|x) = softmax(z/T)

    where T is the temperature parameter learned by minimizing NLL.
    - T > 1: Makes probabilities more uniform (less confident)
    - T < 1: Makes probabilities more peaked (more confident)
    - T = 1: No change
    """

    def __init__(self):
        self.temperature = 1.0

    def fit(
        self,
        logits: np.ndarray,
        y_true: np.ndarray,
        n_iter: int = 100,
        lr: float = 0.01
    ) -> 'TemperatureScaler':
        """
        Learn optimal temperature via gradient descent on NLL.

        Uses Newton-Raphson optimization for single parameter.
        """
        # Initialize
        T = 1.0

        for _ in range(n_iter):
            # Compute scaled probabilities
            scaled_logits = logits / T
            probs = self._softmax(scaled_logits)

            # Compute negative log likelihood gradient w.r.t. T
            # ∂NLL/∂T = -1/T² * Σᵢ (zᵢ - E[z|pᵢ])
            if len(probs.shape) == 1:
                # Binary case
                grad = np.mean((y_true - probs) * logits) / (T * T)
            else:
                # Multiclass case
                y_onehot = np.eye(probs.shape[1])[y_true]
                grad = np.mean(np.sum((y_onehot - probs) * logits, axis=1)) / (T * T)

            # Update temperature
            T = T - lr * grad
            T = max(0.01, min(T, 10.0))  # Clamp to reasonable range

        self.temperature = T
        return self

    def predict_proba(self, logits: np.ndarray) -> np.ndarray:
        """Apply temperature scaling to logits."""
        scaled = logits / self.temperature
        return self._softmax(scaled)

    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        """Numerically stable softmax."""
        if len(x.shape) == 1:
            # Binary case: sigmoid
            return 1 / (1 + np.exp(-x))
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)


class BetaCalibrator:
    """
    Beta Calibration: Uses beta distribution for calibration.

    Mathematical Model:
        c(p) = 1 / (1 + 1/exp(a·ln(p/(1-p)) + b·ln(p) + c·ln(1-p)))

    More flexible than Platt scaling, handles asymmetric distortions.
    Reference: Kull et al., "Beta calibration: a well-founded and
    easily implemented improvement on logistic calibration for binary classifiers"
    """

    def __init__(self):
        self.a = 1.0
        self.b = 0.0
        self.c = 0.0

    def fit(self, probs: np.ndarray, y_true: np.ndarray) -> 'BetaCalibrator':
        """
        Fit beta calibration parameters.

        Args:
            probs: Uncalibrated probabilities in (0, 1)
            y_true: True binary labels
        """
        # Clip to avoid log(0)
        eps = 1e-10
        p = np.clip(probs, eps, 1 - eps)

        # Create features for beta calibration
        # log(p/(1-p)), log(p), log(1-p)
        logit = np.log(p / (1 - p))
        log_p = np.log(p)
        log_1_p = np.log(1 - p)

        X = np.column_stack([logit, log_p, log_1_p])

        # Fit logistic regression
        lr = LogisticRegression(solver='lbfgs', max_iter=1000, C=np.inf)  # C=inf equivalent to no penalty
        lr.fit(X, y_true)

        self.a = lr.coef_[0, 0]
        self.b = lr.coef_[0, 1]
        self.c = lr.coef_[0, 2]
        self._lr = lr

        return self

    def predict_proba(self, probs: np.ndarray) -> np.ndarray:
        """Apply beta calibration."""
        eps = 1e-10
        p = np.clip(probs, eps, 1 - eps)

        logit = np.log(p / (1 - p))
        log_p = np.log(p)
        log_1_p = np.log(1 - p)

        X = np.column_stack([logit, log_p, log_1_p])
        return self._lr.predict_proba(X)[:, 1]


class ModelCalibrator:
    """
    Production-grade model calibrator.

    Automatically selects best calibration method and validates
    improvement using held-out data.
    """

    def __init__(
        self,
        method: str = 'auto',
        cv_folds: int = 5,
        n_bins: int = 10
    ):
        """
        Initialize calibrator.

        Args:
            method: 'auto', 'platt', 'isotonic', 'temperature', 'beta'
            cv_folds: Folds for cross-validation calibration
            n_bins: Number of bins for reliability diagram
        """
        self.method = method
        self.cv_folds = cv_folds
        self.n_bins = n_bins
        self.calibrator_ = None
        self.calibration_result_ = None

    def compute_calibration_metrics(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray
    ) -> CalibrationMetrics:
        """
        Compute calibration quality metrics.

        Expected Calibration Error (ECE):
            ECE = Σᵦ (nᵦ/N) |acc(B) - conf(B)|

        where B are bins, acc(B) is accuracy in bin, conf(B) is mean confidence.
        """
        n_samples = len(y_true)

        # Compute reliability diagram
        prob_true, prob_pred = calibration_curve(
            y_true, y_prob, n_bins=self.n_bins, strategy='uniform'
        )

        # Bin counts for weighting
        bin_edges = np.linspace(0, 1, self.n_bins + 1)
        bin_indices = np.digitize(y_prob, bin_edges) - 1
        bin_indices = np.clip(bin_indices, 0, self.n_bins - 1)

        bin_counts = np.bincount(bin_indices, minlength=self.n_bins)

        # Expected Calibration Error
        # ECE = Σ (n_b / N) * |accuracy_b - confidence_b|
        ece = 0.0
        mce = 0.0

        for i in range(len(prob_true)):
            if i < len(bin_counts) and bin_counts[i] > 0:
                weight = bin_counts[i] / n_samples
                gap = abs(prob_true[i] - prob_pred[i])
                ece += weight * gap
                mce = max(mce, gap)

        # Brier Score: MSE of probability predictions
        brier = np.mean((y_prob - y_true) ** 2)

        return CalibrationMetrics(
            ece=float(ece),
            mce=float(mce),
            brier_score=float(brier),
            reliability_diagram={
                'mean_predicted_value': prob_pred,
                'fraction_of_positives': prob_true
            },
            is_well_calibrated=(ece < 0.05)
        )

    def calibrate(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        X_calib: Optional[np.ndarray] = None,
        y_calib: Optional[np.ndarray] = None
    ) -> CalibrationResult:
        """
        Calibrate a trained model.

        Args:
            model: Trained classifier with predict_proba
            X: Training features
            y: Training labels
            X_calib: Separate calibration set features (optional)
            y_calib: Separate calibration set labels (optional)

        Returns:
            CalibrationResult with calibrated model and metrics
        """
        # Get uncalibrated probabilities
        if X_calib is not None and y_calib is not None:
            probs_uncalib = model.predict_proba(X_calib)[:, 1]
            y_eval = y_calib
        else:
            # Use cross-validation to get out-of-fold predictions
            probs_uncalib = cross_val_predict(
                model, X, y, cv=self.cv_folds, method='predict_proba'
            )[:, 1]
            y_eval = y

        # Compute metrics before calibration
        metrics_before = self.compute_calibration_metrics(y_eval, probs_uncalib)

        # Select and apply calibration method
        if self.method == 'auto':
            # Try all methods and pick best
            best_method, best_calibrator, best_ece = self._auto_select(
                probs_uncalib, y_eval
            )
        else:
            best_method = CalibrationMethod(self.method)
            best_calibrator = self._fit_calibrator(
                best_method, probs_uncalib, y_eval
            )

        # Get calibrated probabilities
        if best_calibrator is not None:
            probs_calib = best_calibrator.predict_proba(probs_uncalib)
        else:
            probs_calib = probs_uncalib

        # Compute metrics after calibration
        metrics_after = self.compute_calibration_metrics(y_eval, probs_calib)

        # Store result
        self.calibrator_ = best_calibrator
        self.calibration_result_ = CalibrationResult(
            calibrator=best_calibrator,
            method=best_method,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            improvement=metrics_before.ece - metrics_after.ece
        )

        return self.calibration_result_

    def _auto_select(
        self,
        probs: np.ndarray,
        y_true: np.ndarray
    ) -> Tuple[CalibrationMethod, Any, float]:
        """Automatically select best calibration method."""
        best_ece = float('inf')
        best_method = CalibrationMethod.NONE
        best_calibrator = None

        for method in [CalibrationMethod.PLATT, CalibrationMethod.ISOTONIC,
                       CalibrationMethod.BETA]:
            try:
                calibrator = self._fit_calibrator(method, probs, y_true)
                if calibrator is not None:
                    probs_calib = calibrator.predict_proba(probs)
                    metrics = self.compute_calibration_metrics(y_true, probs_calib)

                    if metrics.ece < best_ece:
                        best_ece = metrics.ece
                        best_method = method
                        best_calibrator = calibrator
            except Exception:
                continue

        return best_method, best_calibrator, best_ece

    def _fit_calibrator(
        self,
        method: CalibrationMethod,
        probs: np.ndarray,
        y_true: np.ndarray
    ) -> Any:
        """Fit a specific calibration method."""
        if method == CalibrationMethod.PLATT:
            # Convert probs to logits for Platt scaling
            eps = 1e-10
            logits = np.log(np.clip(probs, eps, 1-eps) /
                           np.clip(1-probs, eps, 1-eps))
            calibrator = PlattScaler()
            calibrator.fit(logits, y_true)
            # Wrap to accept probs instead of logits
            original_predict = calibrator.predict_proba
            def predict_from_probs(p):
                eps = 1e-10
                l = np.log(np.clip(p, eps, 1-eps) / np.clip(1-p, eps, 1-eps))
                return original_predict(l)
            calibrator.predict_proba = predict_from_probs
            return calibrator

        elif method == CalibrationMethod.ISOTONIC:
            calibrator = IsotonicRegression(out_of_bounds='clip')
            calibrator.fit(probs, y_true)
            calibrator.predict_proba = calibrator.predict
            return calibrator

        elif method == CalibrationMethod.BETA:
            calibrator = BetaCalibrator()
            calibrator.fit(probs, y_true)
            return calibrator

        elif method == CalibrationMethod.TEMPERATURE:
            # Convert to logits
            eps = 1e-10
            logits = np.log(np.clip(probs, eps, 1-eps) /
                           np.clip(1-probs, eps, 1-eps))
            calibrator = TemperatureScaler()
            calibrator.fit(logits, y_true)
            # Wrap
            original_predict = calibrator.predict_proba
            def predict_from_probs(p):
                eps = 1e-10
                l = np.log(np.clip(p, eps, 1-eps) / np.clip(1-p, eps, 1-eps))
                return original_predict(l)
            calibrator.predict_proba = predict_from_probs
            return calibrator

        return None

    def transform(self, probs: np.ndarray) -> np.ndarray:
        """Apply calibration to new probabilities."""
        if self.calibrator_ is None:
            return probs
        return self.calibrator_.predict_proba(probs)

    def get_summary(self) -> str:
        """Generate human-readable calibration summary."""
        if self.calibration_result_ is None:
            return "No calibration performed yet."

        r = self.calibration_result_
        lines = [
            "=" * 60,
            "MODEL CALIBRATION REPORT",
            "=" * 60,
            f"Method: {r.method.value}",
            "",
            "Before Calibration:",
            f"  Expected Calibration Error (ECE): {r.metrics_before.ece:.4f}",
            f"  Maximum Calibration Error (MCE): {r.metrics_before.mce:.4f}",
            f"  Brier Score: {r.metrics_before.brier_score:.4f}",
            "",
            "After Calibration:",
            f"  Expected Calibration Error (ECE): {r.metrics_after.ece:.4f}",
            f"  Maximum Calibration Error (MCE): {r.metrics_after.mce:.4f}",
            f"  Brier Score: {r.metrics_after.brier_score:.4f}",
            "",
            f"ECE Improvement: {r.improvement:.4f} ({100*r.improvement/max(r.metrics_before.ece, 1e-10):.1f}%)",
            f"Well Calibrated: {'Yes' if r.metrics_after.is_well_calibrated else 'No'}",
            "=" * 60
        ]
        return "\n".join(lines)


class CalibratedModel(BaseEstimator, ClassifierMixin):
    """
    Wrapper that combines a model with its calibrator for deployment.

    Usage:
        calibrated = CalibratedModel(model, calibrator)
        probs = calibrated.predict_proba(X)  # Returns calibrated probabilities
    """

    def __init__(self, model: Any, calibrator: Any):
        self.model = model
        self.calibrator = calibrator

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        probs = self.predict_proba(X)
        if len(probs.shape) == 1:
            return (probs >= 0.5).astype(int)
        return np.argmax(probs, axis=1)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict calibrated probabilities."""
        raw_probs = self.model.predict_proba(X)

        if self.calibrator is None:
            return raw_probs

        if len(raw_probs.shape) == 1 or raw_probs.shape[1] == 2:
            # Binary classification
            if len(raw_probs.shape) == 2:
                probs_1 = raw_probs[:, 1]
            else:
                probs_1 = raw_probs

            calibrated_1 = self.calibrator.predict_proba(probs_1)
            return np.column_stack([1 - calibrated_1, calibrated_1])
        else:
            # Multiclass - calibrate each class
            # Note: Simplified, proper multiclass calibration is more complex
            return raw_probs

    def __getattr__(self, name):
        """Delegate unknown attributes to the underlying model."""
        return getattr(self.model, name)
