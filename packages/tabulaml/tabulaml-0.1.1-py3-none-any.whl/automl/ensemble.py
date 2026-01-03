"""
Model Ensemble and Stacking System

Production-grade ensemble methods for combining multiple models:
1. Simple Averaging - Equal-weight combination
2. Weighted Averaging - Performance-based weights
3. Stacking - Meta-learner on base model predictions
4. Blending - Holdout-based stacking variant

Mathematical Foundation:
- Ensemble reduces variance: Var(avg) = σ²/M for M uncorrelated models
- Optimal weights minimize: w* = argmin E[(y - Σw_i*f_i(x))²]
- Stacking learns optimal combination: g(f_1(x), ..., f_M(x))
- Diversity is key: uncorrelated errors lead to better ensembles
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Union, Callable
from enum import Enum
import warnings
from abc import ABC, abstractmethod


class EnsembleMethod(Enum):
    """Available ensemble methods."""
    AVERAGING = "averaging"
    WEIGHTED = "weighted"
    STACKING = "stacking"
    BLENDING = "blending"
    VOTING = "voting"


@dataclass
class EnsembleModel:
    """Container for an ensemble member."""
    model: Any
    name: str
    weight: float = 1.0
    validation_score: float = 0.0
    diversity_score: float = 0.0

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X)
        raise AttributeError(f"Model {self.name} does not support predict_proba")


@dataclass
class EnsembleResult:
    """Results from ensemble prediction."""
    predictions: np.ndarray
    probabilities: Optional[np.ndarray] = None
    member_predictions: Optional[Dict[str, np.ndarray]] = None
    weights_used: Optional[Dict[str, float]] = None
    ensemble_method: EnsembleMethod = EnsembleMethod.AVERAGING


@dataclass
class EnsembleMetrics:
    """Metrics for ensemble performance analysis."""
    ensemble_score: float
    individual_scores: Dict[str, float]
    improvement_over_best: float
    diversity_measure: float
    correlation_matrix: Optional[np.ndarray] = None


class BaseEnsemble(ABC):
    """Abstract base class for ensemble methods."""

    def __init__(self, task_type: str = "classification"):
        self.task_type = task_type
        self.models: List[EnsembleModel] = []
        self.is_fitted = False

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit the ensemble."""
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        pass

    def add_model(
        self,
        model: Any,
        name: str,
        weight: float = 1.0,
        validation_score: float = 0.0
    ) -> None:
        """Add a model to the ensemble."""
        self.models.append(EnsembleModel(
            model=model,
            name=name,
            weight=weight,
            validation_score=validation_score
        ))

    def get_model_names(self) -> List[str]:
        """Get names of all ensemble members."""
        return [m.name for m in self.models]


class AveragingEnsemble(BaseEnsemble):
    """
    Simple averaging ensemble.

    For regression: ŷ = (1/M) Σ f_i(x)
    For classification: p(y|x) = (1/M) Σ p_i(y|x)

    Effective when models have similar accuracy but different error patterns.
    """

    def __init__(self, task_type: str = "classification"):
        super().__init__(task_type)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """No fitting needed for simple averaging."""
        if not self.models:
            raise ValueError("No models added to ensemble")
        self.is_fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Average predictions from all models."""
        if self.task_type == "classification":
            probas = self.predict_proba(X)
            return np.argmax(probas, axis=1)
        else:
            all_preds = np.array([m.predict(X) for m in self.models])
            return np.mean(all_preds, axis=0)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Average probability predictions."""
        if self.task_type != "classification":
            raise ValueError("predict_proba only for classification")

        all_probas = np.array([m.predict_proba(X) for m in self.models])
        return np.mean(all_probas, axis=0)


class WeightedEnsemble(BaseEnsemble):
    """
    Weighted averaging ensemble with performance-based weights.

    ŷ = Σ w_i * f_i(x) where Σ w_i = 1

    Weight strategies:
    - Performance: w_i ∝ score_i
    - Inverse Error: w_i ∝ 1/error_i
    - Optimized: Solve for optimal weights via regression
    """

    def __init__(
        self,
        task_type: str = "classification",
        weight_strategy: str = "performance"
    ):
        super().__init__(task_type)
        self.weight_strategy = weight_strategy
        self.optimized_weights = None

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None
    ) -> None:
        """
        Fit ensemble weights.

        If validation data provided, optimizes weights to minimize error.
        """
        if not self.models:
            raise ValueError("No models added to ensemble")

        if self.weight_strategy == "optimized" and X_val is not None:
            self._optimize_weights(X_val, y_val)
        elif self.weight_strategy == "performance":
            self._compute_performance_weights()
        elif self.weight_strategy == "inverse_error":
            self._compute_inverse_error_weights()
        else:
            # Equal weights
            for model in self.models:
                model.weight = 1.0 / len(self.models)

        self._normalize_weights()
        self.is_fitted = True

    def _compute_performance_weights(self) -> None:
        """Compute weights proportional to validation scores."""
        scores = np.array([m.validation_score for m in self.models])

        # Handle case where all scores are 0
        if np.sum(scores) == 0:
            weights = np.ones(len(self.models)) / len(self.models)
        else:
            # Softmax-like weighting
            weights = np.exp(scores) / np.sum(np.exp(scores))

        for i, model in enumerate(self.models):
            model.weight = weights[i]

    def _compute_inverse_error_weights(self) -> None:
        """Compute weights inversely proportional to error."""
        scores = np.array([m.validation_score for m in self.models])
        errors = 1 - scores + 1e-10  # Avoid division by zero

        weights = (1 / errors) / np.sum(1 / errors)

        for i, model in enumerate(self.models):
            model.weight = weights[i]

    def _optimize_weights(
        self,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> None:
        """Optimize weights using validation data."""
        try:
            from scipy.optimize import minimize
        except ImportError:
            warnings.warn("scipy required for weight optimization, using performance weights")
            self._compute_performance_weights()
            return

        # Get predictions from all models
        if self.task_type == "classification":
            all_preds = np.array([m.predict_proba(X_val)[:, 1] for m in self.models]).T
        else:
            all_preds = np.array([m.predict(X_val) for m in self.models]).T

        def objective(weights):
            """MSE between weighted prediction and true values."""
            weights = weights / np.sum(weights)  # Normalize
            weighted_pred = np.dot(all_preds, weights)
            if self.task_type == "classification":
                # Log loss for classification
                weighted_pred = np.clip(weighted_pred, 1e-10, 1 - 1e-10)
                return -np.mean(
                    y_val * np.log(weighted_pred) +
                    (1 - y_val) * np.log(1 - weighted_pred)
                )
            else:
                return np.mean((y_val - weighted_pred) ** 2)

        # Initial weights
        n_models = len(self.models)
        x0 = np.ones(n_models) / n_models

        # Constraints: weights sum to 1, all non-negative
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = [(0, 1) for _ in range(n_models)]

        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        self.optimized_weights = result.x / np.sum(result.x)

        for i, model in enumerate(self.models):
            model.weight = self.optimized_weights[i]

    def _normalize_weights(self) -> None:
        """Ensure weights sum to 1."""
        total = sum(m.weight for m in self.models)
        if total > 0:
            for model in self.models:
                model.weight /= total

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Weighted average predictions."""
        if self.task_type == "classification":
            probas = self.predict_proba(X)
            return np.argmax(probas, axis=1)
        else:
            weighted_sum = np.zeros(len(X))
            for model in self.models:
                weighted_sum += model.weight * model.predict(X)
            return weighted_sum

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Weighted average probability predictions."""
        if self.task_type != "classification":
            raise ValueError("predict_proba only for classification")

        weighted_sum = np.zeros((len(X), self.models[0].predict_proba(X).shape[1]))
        for model in self.models:
            weighted_sum += model.weight * model.predict_proba(X)
        return weighted_sum


class StackingEnsemble(BaseEnsemble):
    """
    Stacking ensemble with meta-learner.

    Two-level architecture:
    - Level 0: Base models make predictions
    - Level 1: Meta-learner combines base predictions

    Uses cross-validation to generate meta-features, avoiding overfitting.
    """

    def __init__(
        self,
        task_type: str = "classification",
        meta_learner: Optional[Any] = None,
        cv_folds: int = 5,
        use_probas: bool = True
    ):
        super().__init__(task_type)
        self.meta_learner = meta_learner
        self.cv_folds = cv_folds
        self.use_probas = use_probas and task_type == "classification"
        self._meta_features_fitted = False

    def _get_default_meta_learner(self):
        """Get default meta-learner based on task type."""
        if self.task_type == "classification":
            from sklearn.linear_model import LogisticRegression
            return LogisticRegression(
                C=1.0,
                solver='saga',
                max_iter=1000,
                random_state=42,
                l1_ratio=0  # Equivalent to L2 penalty (sklearn 1.8+)
            )
        else:
            from sklearn.linear_model import Ridge
            return Ridge(alpha=1.0, random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Fit stacking ensemble using cross-validation.

        Generates out-of-fold predictions to train meta-learner.
        """
        if not self.models:
            raise ValueError("No models added to ensemble")

        if self.meta_learner is None:
            self.meta_learner = self._get_default_meta_learner()

        from sklearn.model_selection import KFold

        # Generate meta-features via cross-validation
        n_samples = len(X)
        kf = KFold(n_splits=self.cv_folds, shuffle=True, random_state=42)

        # Initialize meta-features array
        if self.use_probas:
            n_classes = len(np.unique(y))
            meta_features = np.zeros((n_samples, len(self.models) * n_classes))
        else:
            meta_features = np.zeros((n_samples, len(self.models)))

        # Cross-validation to generate out-of-fold predictions
        for train_idx, val_idx in kf.split(X):
            X_train_fold, X_val_fold = X[train_idx], X[val_idx]
            y_train_fold = y[train_idx]

            for i, ensemble_model in enumerate(self.models):
                # Clone and refit model on fold
                from sklearn.base import clone
                fold_model = clone(ensemble_model.model)
                fold_model.fit(X_train_fold, y_train_fold)

                if self.use_probas:
                    preds = fold_model.predict_proba(X_val_fold)
                    start_col = i * preds.shape[1]
                    end_col = start_col + preds.shape[1]
                    meta_features[val_idx, start_col:end_col] = preds
                else:
                    preds = fold_model.predict(X_val_fold)
                    meta_features[val_idx, i] = preds

        # Refit base models on full data
        for ensemble_model in self.models:
            ensemble_model.model.fit(X, y)

        # Fit meta-learner on meta-features
        self.meta_learner.fit(meta_features, y)
        self._meta_features_fitted = True
        self.is_fitted = True

    def _generate_meta_features(self, X: np.ndarray) -> np.ndarray:
        """Generate meta-features from base model predictions."""
        if self.use_probas:
            first_proba = self.models[0].predict_proba(X)
            meta_features = np.zeros((len(X), len(self.models) * first_proba.shape[1]))

            for i, model in enumerate(self.models):
                preds = model.predict_proba(X)
                start_col = i * preds.shape[1]
                end_col = start_col + preds.shape[1]
                meta_features[:, start_col:end_col] = preds
        else:
            meta_features = np.zeros((len(X), len(self.models)))
            for i, model in enumerate(self.models):
                meta_features[:, i] = model.predict(X)

        return meta_features

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict using stacked ensemble."""
        if not self.is_fitted:
            raise ValueError("Ensemble not fitted")

        meta_features = self._generate_meta_features(X)
        return self.meta_learner.predict(meta_features)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities using stacked ensemble."""
        if self.task_type != "classification":
            raise ValueError("predict_proba only for classification")

        if not self.is_fitted:
            raise ValueError("Ensemble not fitted")

        meta_features = self._generate_meta_features(X)

        if hasattr(self.meta_learner, 'predict_proba'):
            return self.meta_learner.predict_proba(meta_features)
        else:
            # Fall back to predictions as probabilities
            preds = self.meta_learner.predict(meta_features)
            probas = np.zeros((len(X), 2))
            probas[:, 1] = preds
            probas[:, 0] = 1 - preds
            return probas


class VotingEnsemble(BaseEnsemble):
    """
    Voting ensemble for classification.

    Strategies:
    - Hard voting: Majority vote of predictions
    - Soft voting: Average of probability predictions
    """

    def __init__(self, voting: str = "soft"):
        super().__init__(task_type="classification")
        self.voting = voting

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """No fitting needed for voting ensemble."""
        if not self.models:
            raise ValueError("No models added to ensemble")
        self.is_fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Vote on predictions."""
        if self.voting == "soft":
            probas = self.predict_proba(X)
            return np.argmax(probas, axis=1)
        else:
            # Hard voting - majority vote
            all_preds = np.array([m.predict(X) for m in self.models])
            from scipy import stats
            return stats.mode(all_preds, axis=0, keepdims=False).mode

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Average probabilities (soft voting)."""
        all_probas = np.array([m.predict_proba(X) for m in self.models])
        return np.mean(all_probas, axis=0)


class EnsembleBuilder:
    """
    Factory class for building and optimizing ensembles.

    Provides automated ensemble construction with:
    - Model selection based on diversity
    - Weight optimization
    - Performance evaluation
    """

    def __init__(
        self,
        task_type: str = "classification",
        method: EnsembleMethod = EnsembleMethod.WEIGHTED
    ):
        self.task_type = task_type
        self.method = method
        self.ensemble = None

    def build(
        self,
        models: List[Tuple[str, Any]],
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        scores: Optional[Dict[str, float]] = None
    ) -> BaseEnsemble:
        """
        Build an ensemble from a list of models.

        Args:
            models: List of (name, model) tuples
            X_train: Training features
            y_train: Training targets
            X_val: Validation features (for weight optimization)
            y_val: Validation targets
            scores: Dict of model_name -> validation_score

        Returns:
            Fitted ensemble
        """
        # Create ensemble based on method
        if self.method == EnsembleMethod.AVERAGING:
            self.ensemble = AveragingEnsemble(self.task_type)
        elif self.method == EnsembleMethod.WEIGHTED:
            self.ensemble = WeightedEnsemble(
                self.task_type,
                weight_strategy="optimized" if X_val is not None else "performance"
            )
        elif self.method == EnsembleMethod.STACKING:
            self.ensemble = StackingEnsemble(self.task_type)
        elif self.method == EnsembleMethod.VOTING:
            self.ensemble = VotingEnsemble()
        else:
            self.ensemble = WeightedEnsemble(self.task_type)

        # Add models to ensemble
        for name, model in models:
            score = scores.get(name, 0.0) if scores else 0.0
            self.ensemble.add_model(model, name, validation_score=score)

        # Fit ensemble
        if isinstance(self.ensemble, WeightedEnsemble) and X_val is not None:
            self.ensemble.fit(X_train, y_train, X_val, y_val)
        else:
            self.ensemble.fit(X_train, y_train)

        return self.ensemble

    def evaluate_diversity(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[float, np.ndarray]:
        """
        Evaluate diversity of ensemble members.

        Uses prediction disagreement and correlation analysis.
        Higher diversity generally leads to better ensemble performance.
        """
        if not self.ensemble or not self.ensemble.models:
            raise ValueError("Build ensemble first")

        # Get predictions from all models
        all_preds = np.array([m.predict(X) for m in self.ensemble.models])

        # Compute prediction correlation matrix
        corr_matrix = np.corrcoef(all_preds)

        # Average pairwise correlation (lower is more diverse)
        n = len(self.ensemble.models)
        if n > 1:
            upper_tri = corr_matrix[np.triu_indices(n, k=1)]
            avg_correlation = np.mean(upper_tri)
        else:
            avg_correlation = 1.0

        # Diversity score: 1 - avg_correlation
        diversity_score = 1 - avg_correlation

        return diversity_score, corr_matrix

    def analyze_ensemble(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray,
        metric_fn: Optional[Callable] = None
    ) -> EnsembleMetrics:
        """
        Analyze ensemble performance and diversity.

        Args:
            X_test: Test features
            y_test: Test targets
            metric_fn: Scoring function (default: accuracy for clf, R² for reg)

        Returns:
            EnsembleMetrics with detailed analysis
        """
        if not self.ensemble:
            raise ValueError("Build ensemble first")

        if metric_fn is None:
            if self.task_type == "classification":
                from sklearn.metrics import accuracy_score
                metric_fn = accuracy_score
            else:
                from sklearn.metrics import r2_score
                metric_fn = r2_score

        # Ensemble score
        ensemble_preds = self.ensemble.predict(X_test)
        ensemble_score = metric_fn(y_test, ensemble_preds)

        # Individual model scores
        individual_scores = {}
        for model in self.ensemble.models:
            preds = model.predict(X_test)
            individual_scores[model.name] = metric_fn(y_test, preds)

        # Best individual model
        best_individual = max(individual_scores.values())
        improvement = ensemble_score - best_individual

        # Diversity analysis
        diversity, corr_matrix = self.evaluate_diversity(X_test, y_test)

        return EnsembleMetrics(
            ensemble_score=ensemble_score,
            individual_scores=individual_scores,
            improvement_over_best=improvement,
            diversity_measure=diversity,
            correlation_matrix=corr_matrix
        )


def select_diverse_models(
    models: List[Tuple[str, Any]],
    X: np.ndarray,
    y: np.ndarray,
    n_select: int = 3,
    min_diversity: float = 0.2
) -> List[Tuple[str, Any]]:
    """
    Select diverse subset of models for ensemble.

    Uses greedy selection to maximize diversity while maintaining quality.

    Args:
        models: List of (name, model) tuples
        X: Validation features
        y: Validation targets
        n_select: Number of models to select
        min_diversity: Minimum required diversity from existing members

    Returns:
        Selected diverse models
    """
    if len(models) <= n_select:
        return models

    # Get predictions from all models
    predictions = {}
    for name, model in models:
        predictions[name] = model.predict(X)

    selected = []
    remaining = list(models)

    # Select first model (best performing)
    from sklearn.metrics import accuracy_score, r2_score

    # Detect task type
    if len(np.unique(y)) <= 10:
        metric = accuracy_score
    else:
        metric = r2_score

    scores = {name: metric(y, predictions[name]) for name, _ in models}
    best_name = max(scores, key=scores.get)

    for name, model in remaining:
        if name == best_name:
            selected.append((name, model))
            remaining.remove((name, model))
            break

    # Greedily add diverse models
    while len(selected) < n_select and remaining:
        best_candidate = None
        best_diversity = -1

        for name, model in remaining:
            # Compute min correlation with selected models
            min_corr = 1.0
            for sel_name, _ in selected:
                corr = np.corrcoef(predictions[name], predictions[sel_name])[0, 1]
                min_corr = min(min_corr, abs(corr))

            diversity = 1 - min_corr

            if diversity > best_diversity and diversity >= min_diversity:
                best_diversity = diversity
                best_candidate = (name, model)

        if best_candidate:
            selected.append(best_candidate)
            remaining.remove(best_candidate)
        else:
            # No diverse model found, add best remaining
            best_remaining = max(remaining, key=lambda x: scores[x[0]])
            selected.append(best_remaining)
            remaining.remove(best_remaining)

    return selected
