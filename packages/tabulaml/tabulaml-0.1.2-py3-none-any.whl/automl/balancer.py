"""
Data Balancer Module

Handles class imbalance using various resampling techniques:
- SMOTE (Synthetic Minority Over-sampling Technique)
- SMOTE-NC (for mixed numerical/categorical data)
- ADASYN (Adaptive Synthetic Sampling)
- Random undersampling
- Combination strategies (SMOTE + Tomek links, SMOTE + ENN)
"""

import numpy as np
from typing import Tuple, Optional, List, Literal
from dataclasses import dataclass

from imblearn.over_sampling import SMOTE, ADASYN, SMOTENC, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler, TomekLinks, EditedNearestNeighbours
from imblearn.combine import SMOTETomek, SMOTEENN


@dataclass
class BalancingResult:
    """Container for balancing results."""
    X_resampled: np.ndarray
    y_resampled: np.ndarray
    strategy_used: str
    original_class_distribution: dict
    new_class_distribution: dict
    samples_before: int
    samples_after: int
    was_applied: bool


class DataBalancer:
    """
    Handles class imbalance for classification tasks using imbalanced-learn.

    Supports multiple resampling strategies and automatically selects
    the most appropriate one based on data characteristics.
    """

    STRATEGY_MAP = {
        'smote': SMOTE,
        'smote_nc': SMOTENC,
        'adasyn': ADASYN,
        'random_over': RandomOverSampler,
        'random_under': RandomUnderSampler,
        'tomek': TomekLinks,
        'enn': EditedNearestNeighbours,
        'smote_tomek': SMOTETomek,
        'smote_enn': SMOTEENN,
    }

    def __init__(
        self,
        strategy: Literal['auto', 'smote', 'smote_nc', 'adasyn',
                          'random_over', 'random_under', 'smote_tomek',
                          'smote_enn', 'none'] = 'auto',
        sampling_ratio: float = 1.0,
        random_state: int = 42,
        k_neighbors: int = 5,
        n_jobs: int = -1
    ):
        """
        Initialize the data balancer.

        Args:
            strategy: Resampling strategy to use. 'auto' will select best strategy.
                - 'smote': Synthetic Minority Over-sampling
                - 'smote_nc': SMOTE for numerical + categorical features
                - 'adasyn': Adaptive synthetic sampling
                - 'random_over': Random oversampling
                - 'random_under': Random undersampling
                - 'smote_tomek': SMOTE + Tomek links cleaning
                - 'smote_enn': SMOTE + Edited Nearest Neighbors cleaning
                - 'none': No resampling
            sampling_ratio: Target ratio of minority to majority class
            random_state: Random seed for reproducibility
            k_neighbors: Number of neighbors for SMOTE-based methods
            n_jobs: Number of parallel jobs
        """
        self.strategy = strategy
        self.sampling_ratio = sampling_ratio
        self.random_state = random_state
        self.k_neighbors = k_neighbors
        self.n_jobs = n_jobs

    def balance(
        self,
        X: np.ndarray,
        y: np.ndarray,
        categorical_features: Optional[List[int]] = None,
        is_imbalanced: bool = True
    ) -> BalancingResult:
        """
        Apply resampling to balance the dataset.

        Args:
            X: Feature matrix
            y: Target vector
            categorical_features: Indices of categorical features (for SMOTE-NC)
            is_imbalanced: Whether the dataset is imbalanced

        Returns:
            BalancingResult with resampled data and metadata
        """
        # Get original class distribution
        unique, counts = np.unique(y, return_counts=True)
        original_distribution = dict(zip(unique.tolist(), counts.tolist()))

        # Don't balance if not imbalanced or strategy is 'none'
        if not is_imbalanced or self.strategy == 'none':
            return BalancingResult(
                X_resampled=X,
                y_resampled=y,
                strategy_used='none',
                original_class_distribution=original_distribution,
                new_class_distribution=original_distribution,
                samples_before=len(y),
                samples_after=len(y),
                was_applied=False
            )

        # Select strategy
        strategy = self._select_strategy(X, y, categorical_features)

        # Get the resampler
        resampler = self._get_resampler(strategy, categorical_features)

        # Apply resampling
        try:
            X_resampled, y_resampled = resampler.fit_resample(X, y)

            # Get new class distribution
            unique_new, counts_new = np.unique(y_resampled, return_counts=True)
            new_distribution = dict(zip(unique_new.tolist(), counts_new.tolist()))

            return BalancingResult(
                X_resampled=X_resampled,
                y_resampled=y_resampled,
                strategy_used=strategy,
                original_class_distribution=original_distribution,
                new_class_distribution=new_distribution,
                samples_before=len(y),
                samples_after=len(y_resampled),
                was_applied=True
            )
        except Exception as e:
            # If resampling fails, return original data
            print(f"Warning: Balancing failed ({strategy}): {e}. Using original data.")
            return BalancingResult(
                X_resampled=X,
                y_resampled=y,
                strategy_used='none (failed)',
                original_class_distribution=original_distribution,
                new_class_distribution=original_distribution,
                samples_before=len(y),
                samples_after=len(y),
                was_applied=False
            )

    def _select_strategy(
        self,
        X: np.ndarray,
        y: np.ndarray,
        categorical_features: Optional[List[int]] = None
    ) -> str:
        """
        Automatically select the best resampling strategy.

        Args:
            X: Feature matrix
            y: Target vector
            categorical_features: Indices of categorical features

        Returns:
            Strategy name
        """
        if self.strategy != 'auto':
            return self.strategy

        n_samples = len(y)
        n_features = X.shape[1]
        unique_classes = len(np.unique(y))
        min_class_count = min(np.bincount(y.astype(int) if y.dtype != object else
                                         np.array([list(np.unique(y)).index(v) for v in y])))

        # For very small minority classes, use random oversampling first
        if min_class_count < self.k_neighbors + 1:
            return 'random_over'

        # For datasets with categorical features, use SMOTE-NC
        if categorical_features and len(categorical_features) > 0:
            return 'smote_nc'

        # For large datasets, use SMOTE + Tomek for better boundaries
        if n_samples > 10000:
            return 'smote_tomek'

        # For multiclass with many classes, ADASYN can be better
        if unique_classes > 3:
            return 'adasyn'

        # Default to SMOTE for most cases
        return 'smote'

    def _get_resampler(
        self,
        strategy: str,
        categorical_features: Optional[List[int]] = None
    ):
        """
        Get the resampler instance for the given strategy.

        Args:
            strategy: Resampling strategy name
            categorical_features: Indices of categorical features

        Returns:
            Resampler instance
        """
        common_params = {
            'random_state': self.random_state,
        }

        if strategy == 'smote':
            return SMOTE(
                k_neighbors=self.k_neighbors,
                **common_params
            )

        elif strategy == 'smote_nc':
            if not categorical_features:
                # Fall back to regular SMOTE if no categorical features
                return SMOTE(k_neighbors=self.k_neighbors, **common_params)
            return SMOTENC(
                categorical_features=categorical_features,
                k_neighbors=self.k_neighbors,
                **common_params
            )

        elif strategy == 'adasyn':
            return ADASYN(
                n_neighbors=self.k_neighbors,
                **common_params
            )

        elif strategy == 'random_over':
            return RandomOverSampler(**common_params)

        elif strategy == 'random_under':
            return RandomUnderSampler(**common_params)

        elif strategy == 'smote_tomek':
            return SMOTETomek(
                smote=SMOTE(k_neighbors=self.k_neighbors, **common_params),
                **common_params
            )

        elif strategy == 'smote_enn':
            return SMOTEENN(
                smote=SMOTE(k_neighbors=self.k_neighbors, **common_params),
                **common_params
            )

        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def get_summary(self, result: BalancingResult) -> str:
        """Generate a human-readable summary of the balancing."""
        lines = [
            "=" * 50,
            "DATA BALANCING SUMMARY",
            "=" * 50,
        ]

        if not result.was_applied:
            lines.append("No balancing applied (dataset is balanced or strategy='none')")
        else:
            lines.extend([
                f"Strategy: {result.strategy_used.upper()}",
                f"Samples before: {result.samples_before:,}",
                f"Samples after: {result.samples_after:,}",
                f"Change: {result.samples_after - result.samples_before:+,} samples",
                "",
                "Original class distribution:",
            ])

            for cls, count in sorted(result.original_class_distribution.items(),
                                    key=lambda x: -x[1]):
                pct = 100 * count / result.samples_before
                lines.append(f"  - Class {cls}: {count:,} ({pct:.1f}%)")

            lines.extend(["", "New class distribution:"])

            for cls, count in sorted(result.new_class_distribution.items(),
                                    key=lambda x: -x[1]):
                pct = 100 * count / result.samples_after
                lines.append(f"  - Class {cls}: {count:,} ({pct:.1f}%)")

        lines.append("=" * 50)

        return "\n".join(lines)
