"""
Preprocessing Pipeline Module

Handles data preprocessing:
- Numerical features: Missing value imputation (mean/median), Feature scaling (StandardScaler)
- Categorical features: Missing value imputation (most frequent), One-Hot Encoding
- High-cardinality handling: Limits categories or drops features
- Combines using ColumnTransformer
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

from .profiler import DataProfile


@dataclass
class PreprocessingResult:
    """Container for preprocessing results."""
    preprocessor: ColumnTransformer
    feature_names: List[str]
    numerical_features: List[str]
    categorical_features: List[str]
    n_features_in: int
    n_features_out: int
    dropped_high_cardinality: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class DataPreprocessor:
    """Builds and applies preprocessing pipelines for ML data."""

    def __init__(
        self,
        numerical_imputation: str = "median",
        scale_numerical: bool = True,
        handle_unknown: str = "ignore",
        sparse_output: bool = False,
        max_categories: int = 50,
        max_cardinality: int = 100
    ):
        """
        Initialize the preprocessor.

        Args:
            numerical_imputation: Strategy for numerical imputation ('mean', 'median', 'most_frequent')
            scale_numerical: Whether to apply StandardScaler to numerical features
            handle_unknown: How to handle unknown categories ('ignore', 'error')
            sparse_output: Whether to output sparse matrix
            max_categories: Maximum categories to keep per feature in OneHotEncoder (rest grouped as 'infrequent')
            max_cardinality: Maximum unique values allowed; features with more are dropped
        """
        self.numerical_imputation = numerical_imputation
        self.scale_numerical = scale_numerical
        self.handle_unknown = handle_unknown
        self.sparse_output = sparse_output
        self.max_categories = max_categories
        self.max_cardinality = max_cardinality

    def build_preprocessor(
        self,
        profile: DataProfile,
        df: pd.DataFrame = None,
        exclude_target: bool = True
    ) -> PreprocessingResult:
        """
        Build a preprocessing pipeline based on data profile.

        Args:
            profile: DataProfile from the profiler
            df: DataFrame to check cardinality (optional but recommended)
            exclude_target: Whether to exclude target column from features

        Returns:
            PreprocessingResult with the preprocessor and metadata
        """
        # Get feature lists, excluding target column
        numerical_features = profile.numerical_columns.copy()
        categorical_features = profile.categorical_columns.copy()
        dropped_high_cardinality = []
        warnings = []

        if exclude_target and profile.target_column:
            if profile.target_column in numerical_features:
                numerical_features.remove(profile.target_column)
            if profile.target_column in categorical_features:
                categorical_features.remove(profile.target_column)

        # Filter out high-cardinality categorical features
        if df is not None and categorical_features:
            filtered_categorical = []
            for col in categorical_features:
                n_unique = df[col].nunique()
                if n_unique > self.max_cardinality:
                    dropped_high_cardinality.append(col)
                    warnings.append(
                        f"Dropped '{col}' ({n_unique:,} unique values) - exceeds max_cardinality={self.max_cardinality}"
                    )
                else:
                    filtered_categorical.append(col)
            categorical_features = filtered_categorical

        # Build numerical pipeline
        numerical_steps = [
            ('imputer', SimpleImputer(strategy=self.numerical_imputation))
        ]
        if self.scale_numerical:
            numerical_steps.append(('scaler', StandardScaler()))

        numerical_pipeline = Pipeline(numerical_steps)

        # Build categorical pipeline with max_categories to limit OneHotEncoder output
        categorical_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(
                handle_unknown=self.handle_unknown,
                sparse_output=self.sparse_output,
                max_categories=self.max_categories,
                min_frequency=0.01  # Ignore categories appearing in < 1% of samples
            ))
        ])

        # Combine with ColumnTransformer
        transformers = []

        if numerical_features:
            transformers.append(('numerical', numerical_pipeline, numerical_features))

        if categorical_features:
            transformers.append(('categorical', categorical_pipeline, categorical_features))

        preprocessor = ColumnTransformer(
            transformers=transformers,
            remainder='drop',
            verbose_feature_names_out=False
        )

        # Calculate expected output features
        n_features_in = len(numerical_features) + len(categorical_features)

        return PreprocessingResult(
            preprocessor=preprocessor,
            feature_names=numerical_features + categorical_features,
            numerical_features=numerical_features,
            categorical_features=categorical_features,
            n_features_in=n_features_in,
            n_features_out=0,  # Will be updated after fitting
            dropped_high_cardinality=dropped_high_cardinality,
            warnings=warnings
        )

    def fit_transform(
        self,
        df: pd.DataFrame,
        profile: DataProfile
    ) -> Tuple[np.ndarray, pd.Series, PreprocessingResult]:
        """
        Build, fit, and transform the data.

        Args:
            df: Input DataFrame
            profile: DataProfile from the profiler

        Returns:
            Tuple of (X_transformed, y, preprocessing_result)
        """
        result = self.build_preprocessor(profile, df=df)

        # Prepare features and target
        feature_cols = result.numerical_features + result.categorical_features
        X = df[feature_cols]
        y = df[profile.target_column] if profile.target_column else None

        # Fit and transform
        X_transformed = result.preprocessor.fit_transform(X)

        # Update output feature count
        if hasattr(X_transformed, 'shape'):
            result.n_features_out = X_transformed.shape[1]

        return X_transformed, y, result

    def get_feature_names_out(
        self,
        preprocessor: ColumnTransformer,
        numerical_features: List[str],
        categorical_features: List[str]
    ) -> List[str]:
        """
        Get output feature names after transformation.

        Args:
            preprocessor: Fitted ColumnTransformer
            numerical_features: List of numerical feature names
            categorical_features: List of categorical feature names

        Returns:
            List of output feature names
        """
        try:
            return list(preprocessor.get_feature_names_out())
        except Exception:
            # Fallback for older sklearn versions
            feature_names = numerical_features.copy()

            # Try to get one-hot encoded names
            try:
                encoder = preprocessor.named_transformers_['categorical'].named_steps['encoder']
                cat_features = encoder.get_feature_names_out(categorical_features)
                feature_names.extend(cat_features)
            except Exception:
                feature_names.extend(categorical_features)

            return feature_names

    def get_summary(self, result: PreprocessingResult) -> str:
        """Generate a human-readable summary of the preprocessing."""
        lines = [
            "=" * 50,
            "PREPROCESSING SUMMARY",
            "=" * 50,
            f"Input features: {result.n_features_in}",
            f"Output features: {result.n_features_out}",
            "",
            f"Numerical features ({len(result.numerical_features)}):",
        ]

        for feat in result.numerical_features:
            lines.append(f"  - {feat}")

        lines.append(f"\nCategorical features ({len(result.categorical_features)}):")

        for feat in result.categorical_features:
            lines.append(f"  - {feat}")

        # Show warnings about dropped features
        if result.dropped_high_cardinality:
            lines.append(f"\nWARNING: Dropped {len(result.dropped_high_cardinality)} high-cardinality feature(s):")
            for col in result.dropped_high_cardinality:
                lines.append(f"  - {col}")

        if result.warnings:
            lines.append("\nNotes:")
            for warning in result.warnings:
                lines.append(f"  ! {warning}")

        lines.append("=" * 50)

        return "\n".join(lines)
