"""
Task Inference Module

Determines the ML task type based on target column characteristics:
- Regression: target is continuous numeric
- Classification: target is categorical or has fewer than 20 unique values
- Binary vs Multiclass classification detection
"""

import pandas as pd
import numpy as np
from typing import Optional
from enum import Enum
from dataclasses import dataclass

from .profiler import DataProfile


class TaskType(Enum):
    """Enumeration of supported ML task types."""
    BINARY_CLASSIFICATION = "binary_classification"
    MULTICLASS_CLASSIFICATION = "multiclass_classification"
    REGRESSION = "regression"


@dataclass
class TaskInfo:
    """Container for task inference results."""
    task_type: TaskType
    n_classes: Optional[int]
    is_binary: bool
    is_multiclass: bool
    is_regression: bool
    target_dtype: str
    reasoning: str


class TaskInferrer:
    """Infers the ML task type from data profile and target column."""

    def __init__(self, classification_threshold: int = 20):
        """
        Initialize the task inferrer.

        Args:
            classification_threshold: Maximum unique values to consider as classification.
                                     Above this, task is treated as regression.
        """
        self.classification_threshold = classification_threshold

    def infer(
        self,
        df: pd.DataFrame,
        profile: DataProfile
    ) -> TaskInfo:
        """
        Infer the ML task type.

        Args:
            df: Input DataFrame
            profile: DataProfile from the profiler

        Returns:
            TaskInfo object with task details
        """
        target_column = profile.target_column

        if target_column is None or target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in DataFrame")

        target_series = df[target_column]
        n_unique = target_series.nunique()
        target_dtype = str(target_series.dtype)

        # Determine task type
        task_type, reasoning = self._determine_task_type(
            target_series, n_unique, target_dtype
        )

        # Set flags
        is_binary = task_type == TaskType.BINARY_CLASSIFICATION
        is_multiclass = task_type == TaskType.MULTICLASS_CLASSIFICATION
        is_regression = task_type == TaskType.REGRESSION
        n_classes = n_unique if not is_regression else None

        return TaskInfo(
            task_type=task_type,
            n_classes=n_classes,
            is_binary=is_binary,
            is_multiclass=is_multiclass,
            is_regression=is_regression,
            target_dtype=target_dtype,
            reasoning=reasoning
        )

    def _determine_task_type(
        self,
        target_series: pd.Series,
        n_unique: int,
        target_dtype: str
    ) -> tuple:
        """
        Determine the task type based on target characteristics.

        Returns:
            Tuple of (TaskType, reasoning string)
        """
        # Check if target is categorical (object/string type)
        if target_series.dtype == 'object' or pd.api.types.is_categorical_dtype(target_series):
            if n_unique == 2:
                return (
                    TaskType.BINARY_CLASSIFICATION,
                    f"Target is categorical with 2 classes"
                )
            else:
                return (
                    TaskType.MULTICLASS_CLASSIFICATION,
                    f"Target is categorical with {n_unique} classes"
                )

        # Check if target is boolean
        if target_series.dtype == 'bool':
            return (
                TaskType.BINARY_CLASSIFICATION,
                "Target is boolean (binary)"
            )

        # For numeric targets, check cardinality
        if pd.api.types.is_numeric_dtype(target_series):
            # Check if values are integers or could be class labels
            if self._is_likely_classification(target_series, n_unique):
                if n_unique == 2:
                    return (
                        TaskType.BINARY_CLASSIFICATION,
                        f"Target is numeric with 2 unique values (binary classification)"
                    )
                else:
                    return (
                        TaskType.MULTICLASS_CLASSIFICATION,
                        f"Target is numeric with {n_unique} unique values (multiclass classification)"
                    )
            else:
                return (
                    TaskType.REGRESSION,
                    f"Target is continuous numeric with {n_unique} unique values"
                )

        # Default to regression for unknown types
        return (
            TaskType.REGRESSION,
            f"Default to regression for dtype: {target_dtype}"
        )

    def _is_likely_classification(
        self,
        target_series: pd.Series,
        n_unique: int
    ) -> bool:
        """
        Determine if a numeric target is likely a classification task.

        Heuristics:
        - Few unique values (< threshold)
        - Integer values only
        - Values look like class labels (0, 1, 2, ...)
        """
        # If too many unique values, it's regression
        if n_unique > self.classification_threshold:
            return False

        # If all values are integers
        try:
            if target_series.dropna().apply(lambda x: x == int(x)).all():
                return True
        except (ValueError, TypeError):
            pass

        # If unique ratio is very low, likely classification
        unique_ratio = n_unique / len(target_series)
        if unique_ratio < 0.05:
            return True

        return False

    def get_summary(self, task_info: TaskInfo) -> str:
        """Generate a human-readable summary of the task inference."""
        lines = [
            "=" * 50,
            "TASK INFERENCE SUMMARY",
            "=" * 50,
            f"Task Type: {task_info.task_type.value}",
            f"Target dtype: {task_info.target_dtype}",
        ]

        if not task_info.is_regression:
            lines.append(f"Number of classes: {task_info.n_classes}")

        lines.extend([
            "",
            f"Reasoning: {task_info.reasoning}",
            "=" * 50
        ])

        return "\n".join(lines)
