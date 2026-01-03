"""
Trainer Module

Implements training strategy:
- 3-fold cross-validation
- Parallel execution (n_jobs=-1)
- Early stopping where supported
- Optional subset training before full training
- Promote top-performing models to full dataset
"""

import os
import sys
import time
import warnings

# Suppress joblib/loky warnings on Windows
if sys.platform == "win32":
    os.environ["LOKY_MAX_CPU_COUNT"] = str(os.cpu_count() or 4)
    os.environ["JOBLIB_START_METHOD"] = "spawn"
    # Use threading backend to avoid resource tracker issues
    try:
        from joblib import parallel_config
        parallel_config(backend="threading")
    except ImportError:
        pass

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="joblib")
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
warnings.filterwarnings("ignore", message=".*resource_tracker.*")
warnings.filterwarnings("ignore", message=".*loky.*")

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from copy import deepcopy

from sklearn.model_selection import cross_val_score, StratifiedKFold, KFold
from sklearn.base import clone

from .task_inference import TaskType, TaskInfo
from .models import ModelCandidate


@dataclass
class TrainingResult:
    """Container for single model training results."""
    model_name: str
    model: Any
    cv_scores: List[float]
    mean_score: float
    std_score: float
    training_time: float
    is_best: bool = False


@dataclass
class TrainingReport:
    """Container for full training report."""
    results: List[TrainingResult] = field(default_factory=list)
    best_model_name: str = ""
    best_model: Any = None
    best_score: float = 0.0
    total_training_time: float = 0.0
    task_type: Optional[TaskType] = None
    scoring_metric: str = ""


class ModelTrainer:
    """Trains and evaluates model candidates."""

    def __init__(
        self,
        cv_folds: int = 3,
        n_jobs: int = -1,
        random_state: int = 42,
        subset_ratio: float = 0.3,
        top_k_models: int = 3,
        verbose: bool = True,
        scoring_override: Optional[str] = None
    ):
        """
        Initialize the trainer.

        Args:
            cv_folds: Number of cross-validation folds
            n_jobs: Number of parallel jobs (-1 for all cores)
            random_state: Random seed for reproducibility
            subset_ratio: Fraction of data for initial subset training (0-1)
            top_k_models: Number of top models to promote to full training
            verbose: Whether to print progress
            scoring_override: Optional scoring metric to use instead of default
                             (e.g., 'recall', 'precision', 'f1' for context-aware training)
        """
        self.cv_folds = cv_folds
        self.n_jobs = n_jobs
        self.random_state = random_state
        self.subset_ratio = subset_ratio
        self.top_k_models = top_k_models
        self.verbose = verbose
        self.scoring_override = scoring_override

    def get_scoring_metric(self, task_info: TaskInfo) -> str:
        """
        Get the appropriate scoring metric for the task.

        If scoring_override is set (for context-aware training), uses that instead.

        Args:
            task_info: TaskInfo from task inference

        Returns:
            Scoring metric string for sklearn
        """
        # Use override if provided (for context-aware training)
        if self.scoring_override and not task_info.is_regression:
            # Map context metrics to sklearn scoring
            metric_map = {
                'recall': 'recall' if task_info.is_binary else 'recall_macro',
                'precision': 'precision' if task_info.is_binary else 'precision_macro',
                'f1': 'f1' if task_info.is_binary else 'f1_macro'
            }
            return metric_map.get(self.scoring_override, self.scoring_override)

        # Default behavior
        if task_info.is_binary:
            return 'roc_auc'
        elif task_info.is_multiclass:
            return 'f1_macro'
        else:  # regression
            return 'neg_root_mean_squared_error'

    def get_cv_splitter(self, task_info: TaskInfo):
        """
        Get the appropriate cross-validation splitter.

        Args:
            task_info: TaskInfo from task inference

        Returns:
            CV splitter object
        """
        if task_info.is_regression:
            return KFold(
                n_splits=self.cv_folds,
                shuffle=True,
                random_state=self.random_state
            )
        else:
            return StratifiedKFold(
                n_splits=self.cv_folds,
                shuffle=True,
                random_state=self.random_state
            )

    def train_single_model(
        self,
        model_candidate: ModelCandidate,
        X: np.ndarray,
        y: np.ndarray,
        task_info: TaskInfo
    ) -> TrainingResult:
        """
        Train and evaluate a single model using cross-validation.

        Args:
            model_candidate: ModelCandidate to train
            X: Feature matrix
            y: Target vector
            task_info: TaskInfo from task inference

        Returns:
            TrainingResult with scores and timing
        """
        scoring = self.get_scoring_metric(task_info)
        cv_splitter = self.get_cv_splitter(task_info)

        if self.verbose:
            print(f"  Training {model_candidate.name}...", end=" ", flush=True)

        start_time = time.time()

        try:
            # Clone the model to avoid state issues
            model = clone(model_candidate.model)

            # Perform cross-validation
            cv_scores = cross_val_score(
                model,
                X, y,
                cv=cv_splitter,
                scoring=scoring,
                n_jobs=self.n_jobs
            )

            training_time = time.time() - start_time

            # For negative metrics, we need to negate for proper comparison
            mean_score = np.mean(cv_scores)
            std_score = np.std(cv_scores)

            if self.verbose:
                print(f"Score: {mean_score:.4f} (+/- {std_score:.4f}) [{training_time:.1f}s]")

            return TrainingResult(
                model_name=model_candidate.name,
                model=model,
                cv_scores=cv_scores.tolist(),
                mean_score=mean_score,
                std_score=std_score,
                training_time=training_time
            )

        except Exception as e:
            training_time = time.time() - start_time
            if self.verbose:
                print(f"FAILED: {str(e)}")

            return TrainingResult(
                model_name=model_candidate.name,
                model=None,
                cv_scores=[],
                mean_score=float('-inf'),
                std_score=0.0,
                training_time=training_time
            )

    def train_all_models(
        self,
        model_candidates: List[ModelCandidate],
        X: np.ndarray,
        y: np.ndarray,
        task_info: TaskInfo,
        use_subset: bool = False
    ) -> TrainingReport:
        """
        Train all model candidates.

        Args:
            model_candidates: List of ModelCandidate objects
            X: Feature matrix
            y: Target vector
            task_info: TaskInfo from task inference
            use_subset: Whether to use subset for initial training

        Returns:
            TrainingReport with all results
        """
        total_start = time.time()
        report = TrainingReport(
            task_type=task_info.task_type,
            scoring_metric=self.get_scoring_metric(task_info)
        )

        # Use subset if requested
        if use_subset and len(X) > 1000:
            X_train, y_train = self._get_subset(X, y, task_info)
            if self.verbose:
                print(f"\nUsing subset of {len(X_train)} samples for initial training")
        else:
            X_train, y_train = X, y

        if self.verbose:
            print(f"\nTraining {len(model_candidates)} models with {self.cv_folds}-fold CV...")
            print("-" * 50)

        # Train each model
        for candidate in model_candidates:
            result = self.train_single_model(candidate, X_train, y_train, task_info)
            report.results.append(result)

        # Find best model
        valid_results = [r for r in report.results if r.model is not None]
        if valid_results:
            best_result = max(valid_results, key=lambda r: r.mean_score)
            best_result.is_best = True
            report.best_model_name = best_result.model_name
            report.best_model = best_result.model
            report.best_score = best_result.mean_score

        report.total_training_time = time.time() - total_start

        if self.verbose:
            print("-" * 50)
            print(f"Best model: {report.best_model_name} (Score: {report.best_score:.4f})")
            print(f"Total training time: {report.total_training_time:.1f}s")

        return report

    def _get_subset(
        self,
        X: np.ndarray,
        y: np.ndarray,
        task_info: TaskInfo
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get a stratified subset of the data.

        Args:
            X: Feature matrix
            y: Target vector
            task_info: TaskInfo from task inference

        Returns:
            Tuple of (X_subset, y_subset)
        """
        n_samples = int(len(X) * self.subset_ratio)
        n_samples = max(n_samples, 100)  # Minimum 100 samples

        if task_info.is_regression:
            # Random sample for regression
            indices = np.random.RandomState(self.random_state).choice(
                len(X), size=n_samples, replace=False
            )
        else:
            # Stratified sample for classification
            from sklearn.model_selection import train_test_split
            indices, _ = train_test_split(
                np.arange(len(X)),
                train_size=n_samples,
                stratify=y,
                random_state=self.random_state
            )

        return X[indices], y.iloc[indices] if hasattr(y, 'iloc') else y[indices]

    def retrain_best_model(
        self,
        best_model: Any,
        X: np.ndarray,
        y: np.ndarray
    ) -> Any:
        """
        Retrain the best model on the full dataset.

        Args:
            best_model: Best model from training
            X: Full feature matrix
            y: Full target vector

        Returns:
            Fitted model
        """
        if self.verbose:
            print("\nRetraining best model on full dataset...")

        start_time = time.time()

        # Clone and fit on full data
        model = clone(best_model)
        model.fit(X, y)

        if self.verbose:
            print(f"Retraining complete in {time.time() - start_time:.1f}s")

        return model

    def get_summary(self, report: TrainingReport) -> str:
        """Generate a human-readable summary of training results."""
        lines = [
            "=" * 60,
            "TRAINING RESULTS",
            "=" * 60,
            f"Task Type: {report.task_type.value if report.task_type else 'Unknown'}",
            f"Scoring Metric: {report.scoring_metric}",
            f"Total Training Time: {report.total_training_time:.1f}s",
            "",
            "Model Rankings:",
            "-" * 60,
        ]

        # Sort by score
        sorted_results = sorted(
            report.results,
            key=lambda r: r.mean_score,
            reverse=True
        )

        for i, result in enumerate(sorted_results, 1):
            star = " *BEST*" if result.is_best else ""
            status = "" if result.model is not None else " (FAILED)"
            lines.append(
                f"{i}. {result.model_name}: {result.mean_score:.4f} "
                f"(+/- {result.std_score:.4f}){star}{status}"
            )

        lines.extend([
            "-" * 60,
            f"Best Model: {report.best_model_name}",
            f"Best Score: {report.best_score:.4f}",
            "=" * 60
        ])

        return "\n".join(lines)
