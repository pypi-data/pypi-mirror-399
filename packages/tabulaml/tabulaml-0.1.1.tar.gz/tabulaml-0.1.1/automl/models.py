"""
Model Candidates Module

Defines model candidates for different ML tasks:

Classification:
- Logistic Regression
- Random Forest Classifier
- Gradient Boosting Classifier
- XGBoost / LightGBM (optional)

Regression:
- Linear Regression
- Ridge / Lasso
- Random Forest Regressor
- Gradient Boosting Regressor
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor
)

from .task_inference import TaskType


@dataclass
class ModelCandidate:
    """Container for a model candidate."""
    name: str
    model: Any
    params: Dict[str, Any]
    supports_early_stopping: bool = False


class ModelFactory:
    """Factory for creating model candidates based on task type."""

    def __init__(
        self,
        random_state: int = 42,
        n_jobs: int = -1,
        use_xgboost: bool = True,
        use_lightgbm: bool = True,
        class_weight: Optional[str] = None
    ):
        """
        Initialize the model factory.

        Args:
            random_state: Random seed for reproducibility
            n_jobs: Number of parallel jobs (-1 for all cores)
            use_xgboost: Whether to include XGBoost models
            use_lightgbm: Whether to include LightGBM models
            class_weight: Class weighting strategy for imbalanced data:
                         - None: No weighting (default)
                         - 'balanced': Automatically adjust weights inversely
                           proportional to class frequencies
                         - 'balanced_subsample': Like 'balanced' but computed
                           for each tree's bootstrap sample (for RF only)
        """
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.use_xgboost = use_xgboost
        self.use_lightgbm = use_lightgbm
        self.class_weight = class_weight

        # Check for optional dependencies
        self._xgboost_available = self._check_xgboost()
        self._lightgbm_available = self._check_lightgbm()

    def _check_xgboost(self) -> bool:
        """Check if XGBoost is available."""
        try:
            import xgboost
            return True
        except ImportError:
            return False

    def _check_lightgbm(self) -> bool:
        """Check if LightGBM is available."""
        try:
            import lightgbm
            return True
        except ImportError:
            return False

    def get_classification_models(
        self,
        is_binary: bool = True
    ) -> List[ModelCandidate]:
        """
        Get classification model candidates.

        Args:
            is_binary: Whether it's binary classification

        Returns:
            List of ModelCandidate objects
        """
        models = []

        # Determine class_weight for sklearn models
        sklearn_class_weight = self.class_weight
        if sklearn_class_weight == 'balanced_subsample':
            # Only Random Forest supports balanced_subsample
            sklearn_class_weight_lr = 'balanced'
            sklearn_class_weight_gb = 'balanced'
        else:
            sklearn_class_weight_lr = sklearn_class_weight
            sklearn_class_weight_gb = sklearn_class_weight

        # Logistic Regression
        # Use l1_ratio=0 instead of deprecated penalty='l2' (sklearn 1.8+)
        models.append(ModelCandidate(
            name="Logistic Regression",
            model=LogisticRegression(
                random_state=self.random_state,
                max_iter=1000,
                class_weight=sklearn_class_weight_lr,
                l1_ratio=0,  # Equivalent to penalty='l2'
                solver='saga'  # saga supports l1_ratio
            ),
            params={
                'C': [0.1, 1.0, 10.0],
                'l1_ratio': [0, 0.5, 1.0]  # 0=L2, 0.5=elastic, 1=L1
            }
        ))

        # Random Forest - supports balanced_subsample
        rf_class_weight = self.class_weight  # Can use balanced_subsample
        models.append(ModelCandidate(
            name="Random Forest",
            model=RandomForestClassifier(
                random_state=self.random_state,
                n_jobs=self.n_jobs,
                n_estimators=100,
                class_weight=rf_class_weight
            ),
            params={
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, None],
                'min_samples_split': [2, 5, 10]
            }
        ))

        # Gradient Boosting - doesn't support class_weight directly
        # but we can use sample_weight during training
        models.append(ModelCandidate(
            name="Gradient Boosting",
            model=GradientBoostingClassifier(
                random_state=self.random_state,
                n_estimators=100
            ),
            params={
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            },
            supports_early_stopping=True
        ))

        # XGBoost - uses scale_pos_weight for binary
        if self.use_xgboost and self._xgboost_available:
            from xgboost import XGBClassifier

            # XGBoost uses scale_pos_weight for binary imbalance
            # For balanced, we'll set it during training based on class ratios
            xgb_params = {
                'random_state': self.random_state,
                'n_jobs': self.n_jobs,
                'n_estimators': 100,
                'eval_metric': 'logloss' if is_binary else 'mlogloss'
            }

            models.append(ModelCandidate(
                name="XGBoost",
                model=XGBClassifier(**xgb_params),
                params={
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                },
                supports_early_stopping=True
            ))

        # LightGBM - uses class_weight parameter
        if self.use_lightgbm and self._lightgbm_available:
            from lightgbm import LGBMClassifier
            models.append(ModelCandidate(
                name="LightGBM",
                model=LGBMClassifier(
                    random_state=self.random_state,
                    n_jobs=self.n_jobs,
                    n_estimators=100,
                    verbose=-1,
                    class_weight=sklearn_class_weight_lr
                ),
                params={
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                },
                supports_early_stopping=True
            ))

        return models

    def get_regression_models(self) -> List[ModelCandidate]:
        """
        Get regression model candidates.

        Returns:
            List of ModelCandidate objects
        """
        models = []

        # Linear Regression
        models.append(ModelCandidate(
            name="Linear Regression",
            model=LinearRegression(n_jobs=self.n_jobs),
            params={}
        ))

        # Ridge Regression
        models.append(ModelCandidate(
            name="Ridge Regression",
            model=Ridge(random_state=self.random_state),
            params={
                'alpha': [0.1, 1.0, 10.0, 100.0]
            }
        ))

        # Lasso Regression
        models.append(ModelCandidate(
            name="Lasso Regression",
            model=Lasso(random_state=self.random_state, max_iter=5000),
            params={
                'alpha': [0.1, 1.0, 10.0, 100.0]
            }
        ))

        # Random Forest
        models.append(ModelCandidate(
            name="Random Forest",
            model=RandomForestRegressor(
                random_state=self.random_state,
                n_jobs=self.n_jobs,
                n_estimators=100
            ),
            params={
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, None],
                'min_samples_split': [2, 5, 10]
            }
        ))

        # Gradient Boosting
        models.append(ModelCandidate(
            name="Gradient Boosting",
            model=GradientBoostingRegressor(
                random_state=self.random_state,
                n_estimators=100
            ),
            params={
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            },
            supports_early_stopping=True
        ))

        # XGBoost
        if self.use_xgboost and self._xgboost_available:
            from xgboost import XGBRegressor
            models.append(ModelCandidate(
                name="XGBoost",
                model=XGBRegressor(
                    random_state=self.random_state,
                    n_jobs=self.n_jobs,
                    n_estimators=100
                ),
                params={
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                },
                supports_early_stopping=True
            ))

        # LightGBM
        if self.use_lightgbm and self._lightgbm_available:
            from lightgbm import LGBMRegressor
            models.append(ModelCandidate(
                name="LightGBM",
                model=LGBMRegressor(
                    random_state=self.random_state,
                    n_jobs=self.n_jobs,
                    n_estimators=100,
                    verbose=-1
                ),
                params={
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                },
                supports_early_stopping=True
            ))

        return models

    def get_models_for_task(self, task_type: TaskType) -> List[ModelCandidate]:
        """
        Get model candidates based on task type.

        Args:
            task_type: The ML task type

        Returns:
            List of ModelCandidate objects
        """
        if task_type == TaskType.BINARY_CLASSIFICATION:
            return self.get_classification_models(is_binary=True)
        elif task_type == TaskType.MULTICLASS_CLASSIFICATION:
            return self.get_classification_models(is_binary=False)
        elif task_type == TaskType.REGRESSION:
            return self.get_regression_models()
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def get_summary(self, models: List[ModelCandidate]) -> str:
        """Generate a human-readable summary of model candidates."""
        lines = [
            "=" * 50,
            "MODEL CANDIDATES",
            "=" * 50,
        ]

        for i, model in enumerate(models, 1):
            early_stop = " (supports early stopping)" if model.supports_early_stopping else ""
            lines.append(f"{i}. {model.name}{early_stop}")

        lines.append("=" * 50)

        return "\n".join(lines)
