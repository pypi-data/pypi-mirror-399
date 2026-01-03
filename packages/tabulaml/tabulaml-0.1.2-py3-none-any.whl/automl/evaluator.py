"""
Evaluator Module

Handles model evaluation:
- Calculate metrics (ROC-AUC, F1-macro, RMSE, R²)
- Rank models by evaluation metric
- Generate evaluation artifacts (confusion matrix, error plots)
- Compute feature importance
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    mean_squared_error,
    mean_absolute_error,
    r2_score
)
from sklearn.model_selection import train_test_split

from .task_inference import TaskType, TaskInfo


@dataclass
class PerClassMetrics:
    """Container for per-class performance metrics."""
    class_name: str
    precision: float
    recall: float
    f1: float
    support: int  # Number of samples in this class


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics."""
    # Classification metrics
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1: Optional[float] = None
    roc_auc: Optional[float] = None
    confusion_matrix: Optional[np.ndarray] = None
    per_class_metrics: Optional[List[PerClassMetrics]] = None  # Per-class breakdown

    # Regression metrics
    rmse: Optional[float] = None
    mae: Optional[float] = None
    r2: Optional[float] = None
    mape: Optional[float] = None


@dataclass
class FeatureImportance:
    """Container for feature importance data."""
    feature_names: List[str]
    importances: List[float]
    importance_type: str = "model"  # 'model' or 'permutation'


@dataclass
class EvaluationResult:
    """Container for full evaluation results."""
    metrics: EvaluationMetrics
    feature_importance: Optional[FeatureImportance] = None
    predictions: Optional[np.ndarray] = None
    probabilities: Optional[np.ndarray] = None
    classification_report_str: Optional[str] = None


class ModelEvaluator:
    """Evaluates trained models and generates metrics."""

    def __init__(
        self,
        test_size: float = 0.2,
        random_state: int = 42
    ):
        """
        Initialize the evaluator.

        Args:
            test_size: Fraction of data for test set
            random_state: Random seed for reproducibility
        """
        self.test_size = test_size
        self.random_state = random_state

    def evaluate(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        task_info: TaskInfo,
        feature_names: Optional[List[str]] = None,
        class_names: Optional[List[str]] = None
    ) -> EvaluationResult:
        """
        Evaluate a trained model.

        Args:
            model: Trained model
            X: Feature matrix
            y: Target vector
            task_info: TaskInfo from task inference
            feature_names: Optional list of feature names
            class_names: Optional list of class names for classification (original label names)

        Returns:
            EvaluationResult with metrics and artifacts
        """
        # Split data for evaluation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y if not task_info.is_regression else None
        )

        # Fit and predict
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        # Get probabilities for classification
        probabilities = None
        if not task_info.is_regression and hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(X_test)

        # Calculate metrics
        if task_info.is_regression:
            metrics = self._calculate_regression_metrics(y_test, predictions)
            classification_report_str = None
        else:
            metrics = self._calculate_classification_metrics(
                y_test, predictions, probabilities, task_info, class_names
            )
            classification_report_str = classification_report(y_test, predictions)

        # Get feature importance
        feature_importance = self._get_feature_importance(model, feature_names)

        return EvaluationResult(
            metrics=metrics,
            feature_importance=feature_importance,
            predictions=predictions,
            probabilities=probabilities,
            classification_report_str=classification_report_str
        )

    def _calculate_classification_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray],
        task_info: TaskInfo,
        class_names: Optional[List[str]] = None
    ) -> EvaluationMetrics:
        """Calculate classification metrics."""
        metrics = EvaluationMetrics()

        metrics.accuracy = accuracy_score(y_true, y_pred)

        # Determine averaging strategy
        average = 'binary' if task_info.is_binary else 'macro'

        metrics.precision = precision_score(y_true, y_pred, average=average, zero_division=0)
        metrics.recall = recall_score(y_true, y_pred, average=average, zero_division=0)
        metrics.f1 = f1_score(y_true, y_pred, average=average, zero_division=0)
        metrics.confusion_matrix = confusion_matrix(y_true, y_pred)

        # Per-class metrics
        try:
            classes = np.unique(y_true)
            per_class_prec = precision_score(y_true, y_pred, average=None, zero_division=0)
            per_class_rec = recall_score(y_true, y_pred, average=None, zero_division=0)
            per_class_f1 = f1_score(y_true, y_pred, average=None, zero_division=0)

            metrics.per_class_metrics = []
            for i, cls in enumerate(classes):
                support = int(np.sum(y_true == cls))
                # Use original class names if provided
                if class_names is not None and int(cls) < len(class_names):
                    display_name = class_names[int(cls)]
                else:
                    display_name = str(cls)
                metrics.per_class_metrics.append(PerClassMetrics(
                    class_name=display_name,
                    precision=float(per_class_prec[i]),
                    recall=float(per_class_rec[i]),
                    f1=float(per_class_f1[i]),
                    support=support
                ))
        except Exception:
            metrics.per_class_metrics = None

        # ROC-AUC
        if y_proba is not None:
            try:
                if task_info.is_binary:
                    metrics.roc_auc = roc_auc_score(y_true, y_proba[:, 1])
                else:
                    metrics.roc_auc = roc_auc_score(
                        y_true, y_proba, multi_class='ovr', average='macro'
                    )
            except Exception:
                metrics.roc_auc = None

        return metrics

    def _calculate_regression_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> EvaluationMetrics:
        """Calculate regression metrics."""
        metrics = EvaluationMetrics()

        metrics.rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        metrics.mae = mean_absolute_error(y_true, y_pred)
        metrics.r2 = r2_score(y_true, y_pred)

        # MAPE (avoid division by zero)
        mask = y_true != 0
        if mask.sum() > 0:
            metrics.mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

        return metrics

    def _get_feature_importance(
        self,
        model: Any,
        feature_names: Optional[List[str]]
    ) -> Optional[FeatureImportance]:
        """Extract feature importance from model."""
        importances = None
        importance_type = "model"

        # Try different attribute names
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_)
            if len(importances.shape) > 1:
                importances = np.mean(importances, axis=0)

        if importances is None:
            return None

        # Generate feature names if not provided
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(len(importances))]

        return FeatureImportance(
            feature_names=list(feature_names),
            importances=list(importances),
            importance_type=importance_type
        )

    def get_metrics_summary(
        self,
        metrics: EvaluationMetrics,
        task_info: TaskInfo
    ) -> str:
        """Generate a human-readable summary of metrics."""
        lines = [
            "=" * 50,
            "EVALUATION METRICS",
            "=" * 50,
        ]

        if task_info.is_regression:
            lines.extend([
                f"RMSE: {metrics.rmse:.4f}",
                f"MAE: {metrics.mae:.4f}",
                f"R²: {metrics.r2:.4f}",
            ])
            if metrics.mape is not None:
                lines.append(f"MAPE: {metrics.mape:.2f}%")
        else:
            lines.extend([
                f"Accuracy: {metrics.accuracy:.4f}",
                f"Precision: {metrics.precision:.4f}",
                f"Recall: {metrics.recall:.4f}",
                f"F1 Score: {metrics.f1:.4f}",
            ])
            if metrics.roc_auc is not None:
                lines.append(f"ROC-AUC: {metrics.roc_auc:.4f}")

            if metrics.confusion_matrix is not None:
                lines.extend([
                    "",
                    "Confusion Matrix:",
                    str(metrics.confusion_matrix)
                ])

        lines.append("=" * 50)

        return "\n".join(lines)

    def get_feature_importance_summary(
        self,
        feature_importance: FeatureImportance,
        top_k: int = 10
    ) -> str:
        """Generate a summary of feature importance."""
        lines = [
            "=" * 50,
            "FEATURE IMPORTANCE",
            "=" * 50,
        ]

        # Sort by importance
        sorted_indices = np.argsort(feature_importance.importances)[::-1]

        for i, idx in enumerate(sorted_indices[:top_k]):
            name = feature_importance.feature_names[idx]
            importance = feature_importance.importances[idx]
            lines.append(f"{i+1}. {name}: {importance:.4f}")

        lines.append("=" * 50)

        return "\n".join(lines)
