"""
Data Profiler Module

Handles data profiling tasks:
- Detect column names and data types
- Identify missing values
- Analyze categorical cardinality
- Infer target column if not provided
- Detect dataset size and class imbalance
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class DataProfile:
    """Container for data profiling results."""
    n_rows: int
    n_cols: int
    column_types: Dict[str, str]
    numerical_columns: List[str]
    categorical_columns: List[str]
    missing_values: Dict[str, int]
    missing_percentages: Dict[str, float]
    cardinality: Dict[str, int]
    target_column: Optional[str]
    target_unique_values: Optional[int]
    class_distribution: Optional[Dict[Any, int]]
    is_imbalanced: bool
    imbalance_ratio: Optional[float]


class DataProfiler:
    """Analyzes CSV data to extract metadata and statistics."""

    def __init__(self, imbalance_threshold: float = 0.2):
        """
        Initialize the profiler.

        Args:
            imbalance_threshold: Minimum ratio of minority class to consider balanced.
                                 Below this threshold, dataset is considered imbalanced.
        """
        self.imbalance_threshold = imbalance_threshold

    def profile(
        self,
        df: pd.DataFrame,
        target_column: Optional[str] = None
    ) -> DataProfile:
        """
        Profile the dataset.

        Args:
            df: Input DataFrame
            target_column: Name of target column (optional, will be inferred if not provided)

        Returns:
            DataProfile object containing all profiling results
        """
        n_rows, n_cols = df.shape

        # Detect column types
        column_types = self._detect_column_types(df)
        numerical_columns = [col for col, dtype in column_types.items() if dtype == 'numerical']
        categorical_columns = [col for col, dtype in column_types.items() if dtype == 'categorical']

        # Analyze missing values
        missing_values = df.isnull().sum().to_dict()
        missing_percentages = {col: (count / n_rows) * 100 for col, count in missing_values.items()}

        # Analyze cardinality
        cardinality = {col: df[col].nunique() for col in df.columns}

        # Infer target column if not provided
        if target_column is None:
            target_column = self._infer_target_column(df, column_types, cardinality)

        # Analyze target column
        target_unique_values = None
        class_distribution = None
        is_imbalanced = False
        imbalance_ratio = None

        if target_column and target_column in df.columns:
            target_unique_values = df[target_column].nunique()
            class_distribution = df[target_column].value_counts().to_dict()

            # Check for class imbalance
            if target_unique_values <= 20:  # Only for classification tasks
                is_imbalanced, imbalance_ratio = self._check_imbalance(class_distribution)

        return DataProfile(
            n_rows=n_rows,
            n_cols=n_cols,
            column_types=column_types,
            numerical_columns=numerical_columns,
            categorical_columns=categorical_columns,
            missing_values=missing_values,
            missing_percentages=missing_percentages,
            cardinality=cardinality,
            target_column=target_column,
            target_unique_values=target_unique_values,
            class_distribution=class_distribution,
            is_imbalanced=is_imbalanced,
            imbalance_ratio=imbalance_ratio
        )

    def _detect_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Detect whether each column is numerical or categorical.

        Returns:
            Dictionary mapping column names to 'numerical' or 'categorical'
        """
        column_types = {}

        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Check if it's actually categorical (low cardinality integers)
                unique_ratio = df[col].nunique() / len(df)
                if df[col].nunique() <= 10 and unique_ratio < 0.05:
                    column_types[col] = 'categorical'
                else:
                    column_types[col] = 'numerical'
            else:
                column_types[col] = 'categorical'

        return column_types

    def _infer_target_column(
        self,
        df: pd.DataFrame,
        column_types: Dict[str, str],
        cardinality: Dict[str, int]
    ) -> Optional[str]:
        """
        Infer the target column based on heuristics.

        Heuristics used:
        1. Last column is often the target
        2. Column named 'target', 'label', 'class', 'y' etc.
        3. Categorical column with reasonable cardinality

        Returns:
            Inferred target column name or None
        """
        # Common target column names
        target_names = ['target', 'label', 'class', 'y', 'output', 'result',
                       'category', 'outcome', 'prediction', 'response']

        # Check for common target names (case-insensitive)
        for col in df.columns:
            if col.lower() in target_names:
                return col

        # Default to last column
        return df.columns[-1]

    def _check_imbalance(
        self,
        class_distribution: Dict[Any, int]
    ) -> Tuple[bool, float]:
        """
        Check if the class distribution is imbalanced.

        Returns:
            Tuple of (is_imbalanced, imbalance_ratio)
        """
        if not class_distribution:
            return False, None

        counts = list(class_distribution.values())
        min_count = min(counts)
        max_count = max(counts)

        if max_count == 0:
            return False, None

        imbalance_ratio = min_count / max_count
        is_imbalanced = imbalance_ratio < self.imbalance_threshold

        return is_imbalanced, imbalance_ratio

    def get_summary(self, profile: DataProfile) -> str:
        """Generate a human-readable summary of the profile."""
        lines = [
            "=" * 50,
            "DATA PROFILE SUMMARY",
            "=" * 50,
            f"Dataset size: {profile.n_rows:,} rows x {profile.n_cols} columns",
            f"Numerical columns: {len(profile.numerical_columns)}",
            f"Categorical columns: {len(profile.categorical_columns)}",
            "",
            "Missing Values:",
        ]

        has_missing = False
        for col, count in profile.missing_values.items():
            if count > 0:
                has_missing = True
                lines.append(f"  - {col}: {count} ({profile.missing_percentages[col]:.1f}%)")

        if not has_missing:
            lines.append("  No missing values")

        lines.extend([
            "",
            f"Target column: {profile.target_column}",
            f"Target unique values: {profile.target_unique_values}",
        ])

        if profile.class_distribution:
            lines.append("Class distribution:")
            for cls, count in sorted(profile.class_distribution.items(), key=lambda x: -x[1]):
                lines.append(f"  - {cls}: {count}")

        if profile.is_imbalanced:
            lines.append(f"\nWARNING: Dataset is imbalanced (ratio: {profile.imbalance_ratio:.2f})")

        lines.append("=" * 50)

        return "\n".join(lines)
