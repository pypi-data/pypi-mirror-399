"""
AutoML Pipeline Module

Main orchestrator that ties together all components:
- Data Profiling
- Task Inference
- Preprocessing
- Class Balancing (for imbalanced datasets)
- Model Training
- Evaluation
- Export
"""

import os
import sys
import warnings

# Suppress joblib/loky resource tracker warnings on Windows
# Use threading backend instead of loky to avoid resource tracker issues
if sys.platform == "win32":
    os.environ["LOKY_MAX_CPU_COUNT"] = str(os.cpu_count() or 4)
    os.environ["JOBLIB_START_METHOD"] = "spawn"
    # Use threading backend to avoid multiprocessing issues on Windows
    from joblib import parallel_config
    parallel_config(backend="threading")

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="joblib")
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.utils.parallel")
warnings.filterwarnings("ignore", message=".*resource_tracker.*")
warnings.filterwarnings("ignore", message=".*loky.*")
warnings.filterwarnings("ignore", message=".*sklearn.utils.parallel.delayed.*")

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Literal, List
from pathlib import Path

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

from .profiler import DataProfiler, DataProfile
from .task_inference import TaskInferrer, TaskInfo
from .preprocessing import DataPreprocessor, PreprocessingResult
from .balancer import DataBalancer, BalancingResult
from .models import ModelFactory
from .trainer import ModelTrainer, TrainingReport
from .evaluator import ModelEvaluator, EvaluationResult, FeatureImportance
from .exporter import ModelExporter, ExportPaths
from .progress import ProgressBar, QuietProgress
from .business_context import (
    BusinessContext, CONTEXT_CONFIGS, ThresholdOptimizer,
    ThresholdResult, get_scoring_metric
)
from .leakage_detector import LeakageDetector, LeakageReport, LeakageRisk
from .readiness_scorer import ReadinessScorer, ReadinessScore, ReadinessLevel
from .calibration import ModelCalibrator, CalibrationResult
from .statistical_inference import ClassificationMetricsCI, RegressionMetricsCI, ConfidenceInterval
from .drift_detection import DriftDetector, DriftReport
from .uncertainty import UncertaintyQuantifier, UncertaintyReport
from .ensemble import EnsembleBuilder, EnsembleMethod, EnsembleMetrics
from .gates import (
    GateRunner, GateContext, GateReport, ModelVerdict,
    format_gate_report, get_verdict_display, get_verdict_emoji
)


class AutoMLPipeline:
    """
    Main AutoML pipeline that orchestrates the full ML workflow.

    Usage:
        pipeline = AutoMLPipeline()
        results = pipeline.run("data.csv", target_column="target")
    """

    def __init__(
        self,
        output_dir: str = "outputs",
        random_state: int = 42,
        n_jobs: int = -1,
        cv_folds: int = 3,
        test_size: float = 0.2,
        use_xgboost: bool = True,
        use_lightgbm: bool = True,
        balance_classes: bool = True,
        balance_strategy: Literal['auto', 'smote', 'smote_nc', 'adasyn',
                                  'random_over', 'random_under', 'smote_tomek',
                                  'smote_enn', 'none'] = 'auto',
        class_weight: Optional[str] = None,
        verbose: bool = False,
        quiet: bool = False,
        context: Optional[str] = None,
        calibrate_probabilities: bool = False,
        compute_confidence_intervals: bool = False,
        enable_ensemble: bool = False,
        ensemble_method: str = "weighted",
        save_drift_baseline: bool = False,
        drop_leaked_features: bool = True,
        aggressive_leakage_drop: bool = False
    ):
        """
        Initialize the AutoML pipeline.

        Args:
            output_dir: Directory for output files
            random_state: Random seed for reproducibility
            n_jobs: Number of parallel jobs (-1 for all cores)
            cv_folds: Number of cross-validation folds
            test_size: Fraction of data to hold out for final evaluation (0.0 to 1.0)
            use_xgboost: Whether to include XGBoost models
            use_lightgbm: Whether to include LightGBM models
            balance_classes: Whether to apply class balancing for imbalanced datasets
            balance_strategy: Strategy for class balancing ('auto', 'smote', etc.)
            class_weight: Class weighting for models ('balanced' or None)
            verbose: Show detailed technical output (default: False)
            quiet: Completely silent mode - no output at all (default: False)
            context: Business context for optimization. Options:
                     'fraud_detection', 'churn_prediction', 'medical_diagnosis',
                     'spam_detection', 'loan_approval', 'marketing_campaign',
                     'quality_control'. Optimizes for context-specific metrics.
            calibrate_probabilities: Apply Platt/isotonic calibration for reliable probabilities
            compute_confidence_intervals: Calculate bootstrap confidence intervals for metrics
            enable_ensemble: Build ensemble from trained models (weighted average/stacking)
            ensemble_method: 'averaging', 'weighted', 'stacking', or 'voting'
            save_drift_baseline: Save feature distributions for production drift monitoring
            drop_leaked_features: Automatically drop HIGH/CRITICAL risk features (default: True)
            aggressive_leakage_drop: Also drop MEDIUM risk features (may cause false positives)

        Display modes:
            - Default (verbose=False, quiet=False): Show progress bar only
            - Verbose (verbose=True): Show detailed technical output
            - Quiet (quiet=True): No output at all
        """
        self.output_dir = output_dir
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.cv_folds = cv_folds
        self.test_size = test_size
        self.use_xgboost = use_xgboost
        self.use_lightgbm = use_lightgbm
        self.balance_classes = balance_classes
        self.balance_strategy = balance_strategy
        self.class_weight = class_weight
        self.verbose = verbose
        self.quiet = quiet

        # Production features
        self.calibrate_probabilities = calibrate_probabilities
        self.compute_confidence_intervals = compute_confidence_intervals
        self.enable_ensemble = enable_ensemble
        self.ensemble_method = ensemble_method
        self.save_drift_baseline = save_drift_baseline
        self.drop_leaked_features = drop_leaked_features
        self.aggressive_leakage_drop = aggressive_leakage_drop
        self.dropped_features: List[str] = []  # Track dropped leaked features

        # Parse and store business context
        self.context: Optional[BusinessContext] = None
        self.context_config = None
        self.scoring_override = None
        if context:
            try:
                self.context = BusinessContext(context)
                self.context_config = CONTEXT_CONFIGS.get(self.context)
                self.scoring_override = get_scoring_metric(self.context)
            except ValueError:
                raise ValueError(
                    f"Unknown context: '{context}'. Valid options: "
                    f"{', '.join(c.value for c in BusinessContext if c != BusinessContext.CUSTOM)}"
                )

        # Initialize progress display
        # Default: progress bar only
        # Verbose: detailed text output (no progress bar)
        # Quiet: no output at all
        if quiet:
            self.progress = QuietProgress()
        elif verbose:
            self.progress = QuietProgress()  # Verbose mode uses print statements
        else:
            self.progress = ProgressBar(total_steps=9)

        # Initialize components
        self.profiler = DataProfiler()
        self.task_inferrer = TaskInferrer()
        self.preprocessor = DataPreprocessor()
        self.balancer = DataBalancer(
            strategy=balance_strategy,
            random_state=random_state,
            n_jobs=n_jobs
        )
        self.model_factory = ModelFactory(
            random_state=random_state,
            n_jobs=n_jobs,
            use_xgboost=use_xgboost,
            use_lightgbm=use_lightgbm,
            class_weight=class_weight
        )
        self.trainer = ModelTrainer(
            cv_folds=cv_folds,
            n_jobs=n_jobs,
            random_state=random_state,
            verbose=verbose,
            scoring_override=self.scoring_override  # Context-specific metric
        )
        self.evaluator = ModelEvaluator(random_state=random_state)
        self.exporter = ModelExporter(output_dir=output_dir)

        # Store results
        self.profile: Optional[DataProfile] = None
        self.task_info: Optional[TaskInfo] = None
        self.preprocessing_result: Optional[PreprocessingResult] = None
        self.balancing_result: Optional[BalancingResult] = None
        self.training_report: Optional[TrainingReport] = None
        self.evaluation_result: Optional[EvaluationResult] = None
        self.export_paths: Optional[ExportPaths] = None
        self.label_encoder: Optional[LabelEncoder] = None  # For encoding string labels
        self.threshold_result: Optional[ThresholdResult] = None  # For context-aware threshold
        self.leakage_report: Optional[LeakageReport] = None  # Leakage detection results
        self.readiness_score: Optional[ReadinessScore] = None  # Production readiness assessment

        # Production feature results
        self.calibration_result: Optional[CalibrationResult] = None
        self.confidence_intervals: Optional[Dict[str, ConfidenceInterval]] = None
        self.drift_baseline: Optional[DriftReport] = None
        self.uncertainty_report: Optional[UncertaintyReport] = None
        self.ensemble_metrics: Optional[EnsembleMetrics] = None
        self.gate_report: Optional[GateReport] = None

        # Initialize detection/scoring components
        self.leakage_detector = LeakageDetector()
        self.readiness_scorer = ReadinessScorer()
        self.gate_runner = GateRunner()

        # Initialize production feature components
        self.model_calibrator = ModelCalibrator()
        self.drift_detector = DriftDetector()
        self.uncertainty_quantifier = UncertaintyQuantifier(confidence_level=0.9)

    def run(
        self,
        data_path: str,
        target_column: Optional[str] = None,
        run_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the full AutoML pipeline.

        Args:
            data_path: Path to CSV file
            target_column: Name of target column (optional, will be inferred)
            run_name: Optional name for this run

        Returns:
            Dictionary with all results and paths
        """
        # Start progress bar
        self.progress.start("Initializing...")

        if self.verbose:
            print("=" * 60)
            print("TabuLaML - Tabular Machine Learning")
            print("=" * 60)

        # Step 1: Load data
        self.progress.step_loading()
        if self.verbose:
            print(f"\n[1/9] Loading data from {data_path}...")

        # Auto-detect delimiter (handles semicolon-separated files like UCI datasets)
        df = self._load_csv_smart(data_path)

        if self.verbose:
            print(f"Loaded {len(df):,} rows x {len(df.columns)} columns")

        # Step 2: Profile data
        self.progress.step_profiling()
        if self.verbose:
            print("\n[2/9] Profiling data...")

        self.profile = self.profiler.profile(df, target_column)

        if self.verbose:
            print(self.profiler.get_summary(self.profile))

        # Step 3: Infer task type
        self.progress.step_inference()
        if self.verbose:
            print("\n[3/9] Inferring task type...")

        self.task_info = self.task_inferrer.infer(df, self.profile)

        if self.verbose:
            print(self.task_inferrer.get_summary(self.task_info))

        # Run leakage detection on the dataset
        target_col = self.profile.target_column
        self.leakage_report = self.leakage_detector.detect(df, target_col)

        if self.verbose and self.leakage_report.warnings:
            print("\n" + self.leakage_detector.get_summary(self.leakage_report))
        elif self.leakage_report.has_critical_issues and not self.quiet:
            # Always warn about critical leakage issues
            print("\n  WARNING: Potential data leakage detected!")
            for feature in self.leakage_report.high_risk_features[:3]:
                print(f"    - {feature}")

        # Drop leaked features if enabled
        # Default: drop HIGH/CRITICAL only; aggressive mode also drops MEDIUM
        if self.drop_leaked_features:
            if self.aggressive_leakage_drop:
                features_to_drop = [f for f in self.leakage_report.all_risky_features if f in df.columns]
            else:
                features_to_drop = [f for f in self.leakage_report.high_risk_features if f in df.columns]

            if features_to_drop:
                df = df.drop(columns=features_to_drop)
                self.dropped_features = features_to_drop

                # Update the profile to reflect dropped columns
                self.profile.numerical_columns = [c for c in self.profile.numerical_columns if c not in features_to_drop]
                self.profile.categorical_columns = [c for c in self.profile.categorical_columns if c not in features_to_drop]
                self.profile.column_types = {k: v for k, v in self.profile.column_types.items() if k not in features_to_drop}
                self.profile.n_cols = len(df.columns)

                if not self.quiet:
                    # Group by risk level for clarity
                    critical = [f for f in features_to_drop if f in self.leakage_report.high_risk_features]
                    medium = [f for f in features_to_drop if f in self.leakage_report.medium_risk_features]
                    print(f"\n  Dropped {len(features_to_drop)} risky feature(s):")
                    if critical:
                        print(f"    HIGH/CRITICAL: {', '.join(critical)}")
                    if medium:
                        print(f"    MEDIUM: {', '.join(medium)}")

        # Step 4: Split into train/test sets BEFORE preprocessing
        # This prevents data leakage - test set is never seen during model selection
        self.progress.step_splitting()
        if self.verbose:
            print("\n[4/9] Splitting data into train/test sets...")

        # Separate features and target
        target_col = self.profile.target_column
        X_df = df.drop(columns=[target_col])
        y_series = df[target_col]

        # Encode labels if target is non-numeric (required for XGBoost, etc.)
        if not self.task_info.is_regression:
            y_values = y_series.values
            if not np.issubdtype(np.array(y_values).dtype, np.number):
                self.label_encoder = LabelEncoder()
                y_encoded = self.label_encoder.fit_transform(y_values)
                if self.verbose:
                    print(f"Encoded {len(self.label_encoder.classes_)} class labels:")
                    for i, label in enumerate(self.label_encoder.classes_):
                        print(f"  {i}: {label}")
            else:
                y_encoded = y_values
        else:
            y_encoded = y_series.values

        # Split into train/test (stratified for classification)
        stratify = y_encoded if not self.task_info.is_regression else None
        X_train_df, X_test_df, y_train, y_test = train_test_split(
            X_df, y_encoded,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=stratify
        )

        if self.verbose:
            print(f"Train set: {len(X_train_df):,} samples ({100*(1-self.test_size):.0f}%)")
            print(f"Test set:  {len(X_test_df):,} samples ({100*self.test_size:.0f}%) - held out for final evaluation")

        # Step 5: Preprocess data (fit on train, transform both)
        self.progress.step_preprocessing()
        if self.verbose:
            print("\n[5/9] Preprocessing data...")

        # Create a temporary dataframe for preprocessing (train only)
        train_df_for_preprocess = X_train_df.copy()
        train_df_for_preprocess[target_col] = y_train

        # Fit preprocessor on training data only
        X_train, _, self.preprocessing_result = self.preprocessor.fit_transform(
            train_df_for_preprocess, self.profile
        )

        # Transform test data using fitted preprocessor
        X_test = self.preprocessing_result.preprocessor.transform(X_test_df)

        if self.verbose:
            print(self.preprocessor.get_summary(self.preprocessing_result))

        # Step 6: Balance classes (if imbalanced and classification task)
        # Only balance the TRAINING set, not the test set
        self.progress.step_balancing()
        if self.verbose:
            print("\n[6/9] Balancing classes...")

        should_balance = (
            self.balance_classes and
            self.profile.is_imbalanced and
            not self.task_info.is_regression
        )

        if should_balance:
            self.balancing_result = self.balancer.balance(
                X_train, y_train,
                categorical_features=None,
                is_imbalanced=self.profile.is_imbalanced
            )

            # Use balanced data for training
            X_train_balanced = self.balancing_result.X_resampled
            y_train_balanced = self.balancing_result.y_resampled

            if self.verbose:
                print(self.balancer.get_summary(self.balancing_result))
        else:
            self.balancing_result = BalancingResult(
                X_resampled=X_train,
                y_resampled=y_train,
                strategy_used='none',
                original_class_distribution={},
                new_class_distribution={},
                samples_before=len(y_train),
                samples_after=len(y_train),
                was_applied=False
            )
            X_train_balanced = X_train
            y_train_balanced = y_train

            if self.verbose:
                if self.task_info.is_regression:
                    print("Skipping balancing (regression task)")
                elif not self.profile.is_imbalanced:
                    print("Skipping balancing (dataset is balanced)")
                else:
                    print("Skipping balancing (disabled)")

        # Step 7: Get model candidates and train using CV on training set only
        self.progress.step_training()
        if self.verbose:
            print("\n[7/9] Training models...")

        model_candidates = self.model_factory.get_models_for_task(
            self.task_info.task_type
        )

        if self.verbose:
            print(self.model_factory.get_summary(model_candidates))

        # Train using cross-validation on training set only (balanced if applicable)
        self.training_report = self.trainer.train_all_models(
            model_candidates, X_train_balanced, y_train_balanced, self.task_info
        )

        if self.verbose:
            print(self.trainer.get_summary(self.training_report))

        # Step 8: Retrain best model on full training data and evaluate on held-out test set
        self.progress.step_evaluating()
        if self.verbose:
            print("\n[8/9] Evaluating best model on held-out test set...")

        # Retrain on full training data (balanced)
        best_model = self.trainer.retrain_best_model(
            self.training_report.best_model, X_train_balanced, y_train_balanced
        )

        # Context-aware threshold optimization (for binary classification)
        optimal_threshold = 0.5  # Default threshold
        if (self.context and not self.task_info.is_regression and
            self.task_info.is_binary and hasattr(best_model, 'predict_proba')):

            if self.verbose:
                print(f"\nOptimizing threshold for {self.context_config.name}...")
                print(f"Priority metric: {self.context_config.priority_metric}")

            # Get probabilities on test set for threshold tuning
            test_proba = best_model.predict_proba(X_test)[:, 1]

            # Optimize threshold for the business context
            threshold_optimizer = ThresholdOptimizer(self.context)
            self.threshold_result = threshold_optimizer.optimize(y_test, test_proba)
            optimal_threshold = self.threshold_result.optimal_threshold

            if self.verbose:
                print(f"Optimal threshold: {optimal_threshold:.2f} (default: 0.50)")
                print(f"{self.threshold_result.metric_name.capitalize()} improvement: "
                      f"{self.threshold_result.metric_at_default:.4f} -> "
                      f"{self.threshold_result.metric_at_optimal:.4f} "
                      f"(+{self.threshold_result.improvement:.4f})")

        # Get feature names for importance
        feature_names = self.preprocessor.get_feature_names_out(
            self.preprocessing_result.preprocessor,
            self.preprocessing_result.numerical_features,
            self.preprocessing_result.categorical_features
        )

        # Get original class names if labels were encoded
        class_names = None
        if self.label_encoder is not None:
            class_names = list(self.label_encoder.classes_)

        # Evaluate on the held-out test set (never seen during training/CV)
        self.evaluation_result = self._evaluate_on_test_set(
            best_model, X_test, y_test, feature_names, class_names,
            threshold=optimal_threshold
        )

        if self.verbose:
            print(self.evaluator.get_metrics_summary(
                self.evaluation_result.metrics, self.task_info
            ))
            if self.evaluation_result.feature_importance:
                print(self.evaluator.get_feature_importance_summary(
                    self.evaluation_result.feature_importance
                ))

        # Production Readiness Assessment
        # Build feature importance dict for readiness scoring
        feature_importance_dict = None
        if self.evaluation_result.feature_importance:
            feature_importance_dict = dict(zip(
                self.evaluation_result.feature_importance.feature_names,
                self.evaluation_result.feature_importance.importances
            ))

        # Get class distribution for classification
        class_distribution = None
        if not self.task_info.is_regression:
            unique, counts = np.unique(y_train, return_counts=True)
            class_distribution = dict(zip(unique.tolist(), counts.tolist()))

        # Calculate readiness score
        test_score = (
            self.evaluation_result.metrics.f1 or
            self.evaluation_result.metrics.r2 or
            0.0
        )

        self.readiness_score = self.readiness_scorer.score(
            n_samples=len(df),
            n_features=len(df.columns) - 1,
            class_distribution=class_distribution,
            missing_ratio=self.profile.missing_ratio if hasattr(self.profile, 'missing_ratio') else 0.0,
            leakage_report=self.leakage_report,
            cv_score=self.training_report.best_score,
            test_score=test_score,
            feature_importance=feature_importance_dict,
            is_regression=self.task_info.is_regression
        )

        if self.verbose:
            print("\n" + self.readiness_scorer.get_summary(self.readiness_score))
        elif not self.quiet:
            # Show brief readiness status
            print(f"\n  Readiness: {self.readiness_score.overall_score:.0f}/100 ({self.readiness_score.readiness_level.value.upper()})")

        # Run production gates for final verdict
        self.gate_report = self._run_production_gates(df, y_train, X_test, y_test)

        if self.verbose:
            print("\n" + format_gate_report(self.gate_report))
        elif not self.quiet:
            # Show brief verdict
            verdict_str = get_verdict_display(self.gate_report.verdict)
            verdict_icon = get_verdict_emoji(self.gate_report.verdict)
            print(f"  Verdict: {verdict_icon} {verdict_str} (Trust: {self.gate_report.trust_score:.0f}/100)")

        # Production Features: Calibration, Confidence Intervals, Drift Baseline
        self._apply_production_features(
            best_model, X_train_balanced, y_train_balanced,
            X_test, y_test, self.task_info.is_regression
        )

        # Step 9: Export model and reports
        self.progress.step_exporting()
        if self.verbose:
            print("\n[9/9] Exporting model and reports...")

        self.export_paths = self.exporter.export_all(
            model=best_model,
            preprocessor=self.preprocessing_result.preprocessor,
            profile=self.profile,
            task_info=self.task_info,
            training_report=self.training_report,
            evaluation_result=self.evaluation_result,
            run_name=run_name
        )

        # Complete progress bar
        self.progress.complete("Training complete!")

        # Show output summary (only in default progress bar mode)
        if not self.quiet and not self.verbose:
            print(f"\n  Best Model: {self.training_report.best_model_name}")
            if self.context_config:
                print(f"  Context: {self.context_config.name} (optimizing {self.context_config.priority_metric})")
            if self.threshold_result and self.threshold_result.optimal_threshold != 0.5:
                print(f"  Threshold: {self.threshold_result.optimal_threshold:.2f}")
            if self.evaluation_result.metrics.f1:
                print(f"  Test F1 Score: {self.evaluation_result.metrics.f1:.4f}")
            elif self.evaluation_result.metrics.r2:
                print(f"  Test R2 Score: {self.evaluation_result.metrics.r2:.4f}")
            print(f"\n  Output files:")
            print(f"    Model:  {self.export_paths.model_path}")
            print(f"    Report: {self.export_paths.report_html_path}")

        if self.verbose:
            print(f"\nExported files:")
            print(f"  Model: {self.export_paths.model_path}")
            print(f"  Report (JSON): {self.export_paths.report_json_path}")
            print(f"  Report (HTML): {self.export_paths.report_html_path}")
            if self.export_paths.confusion_matrix_path:
                print(f"  Confusion Matrix: {self.export_paths.confusion_matrix_path}")
            if self.export_paths.feature_importance_path:
                print(f"  Feature Importance: {self.export_paths.feature_importance_path}")

            print("\n" + "=" * 60)
            print("TRAINING COMPLETE")
            print("=" * 60)

        return {
            'profile': self.profile,
            'task_info': self.task_info,
            'preprocessing_result': self.preprocessing_result,
            'balancing_result': self.balancing_result,
            'training_report': self.training_report,
            'evaluation_result': self.evaluation_result,
            'export_paths': self.export_paths,
            'best_model_name': self.training_report.best_model_name,
            'best_score': self.training_report.best_score,
            'context': self.context.value if self.context else None,
            'context_config': self.context_config,
            'threshold_result': self.threshold_result,
            'leakage_report': self.leakage_report,
            'readiness_score': self.readiness_score,
            'dropped_features': self.dropped_features,
            # Production features
            'calibration_result': self.calibration_result,
            'confidence_intervals': self.confidence_intervals,
            'drift_baseline': self.drift_baseline,
            'uncertainty_report': self.uncertainty_report,
            'ensemble_metrics': self.ensemble_metrics,
            'gate_report': self.gate_report
        }

    def _load_csv_smart(self, file_path: str) -> pd.DataFrame:
        """
        Load CSV with automatic delimiter detection.

        Handles common delimiters: comma, semicolon, tab.
        This is important for UCI datasets which often use semicolons.

        Args:
            file_path: Path to CSV file

        Returns:
            DataFrame with properly parsed columns
        """
        import csv

        # First, try to detect the delimiter
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            # Read first few lines to detect delimiter
            sample = f.read(4096)

        # Use csv.Sniffer to detect delimiter
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ','  # Default to comma

        # Load with detected delimiter
        df = pd.read_csv(file_path, delimiter=delimiter)

        # If we still have only 1 column and it contains delimiters, try common ones
        if len(df.columns) == 1:
            col_name = df.columns[0]
            if ';' in col_name:
                df = pd.read_csv(file_path, delimiter=';')
            elif '\t' in col_name:
                df = pd.read_csv(file_path, delimiter='\t')

        if self.verbose and delimiter != ',':
            print(f"Detected delimiter: '{delimiter}'")

        return df

    def predict(
        self,
        data: pd.DataFrame,
        model_path: Optional[str] = None
    ) -> np.ndarray:
        """
        Make predictions using a trained model.

        Args:
            data: DataFrame with features (same format as training data)
            model_path: Path to saved model (uses last trained if None)

        Returns:
            Predictions array
        """
        if model_path:
            model_bundle = self.exporter.load_model(model_path)
            model = model_bundle['model']
            preprocessor = model_bundle['preprocessor']
        else:
            if self.training_report is None:
                raise ValueError("No trained model available. Run pipeline first or provide model_path.")

            # Use the current session's model and preprocessor
            model = self.training_report.best_model
            preprocessor = self.preprocessing_result.preprocessor

        # Preprocess input data
        X = preprocessor.transform(data)

        # Make predictions
        return model.predict(X)

    def predict_proba(
        self,
        data: pd.DataFrame,
        model_path: Optional[str] = None
    ) -> np.ndarray:
        """
        Get prediction probabilities (classification only).

        Args:
            data: DataFrame with features
            model_path: Path to saved model (uses last trained if None)

        Returns:
            Probability array
        """
        if model_path:
            model_bundle = self.exporter.load_model(model_path)
            model = model_bundle['model']
            preprocessor = model_bundle['preprocessor']
        else:
            if self.training_report is None:
                raise ValueError("No trained model available.")
            model = self.training_report.best_model
            preprocessor = self.preprocessing_result.preprocessor

        if not hasattr(model, 'predict_proba'):
            raise ValueError("Model does not support probability predictions")

        X = preprocessor.transform(data)
        return model.predict_proba(X)

    def _evaluate_on_test_set(
        self,
        model: Any,
        X_test: np.ndarray,
        y_test: np.ndarray,
        feature_names: list,
        class_names: Optional[list] = None,
        threshold: float = 0.5
    ) -> EvaluationResult:
        """
        Evaluate a trained model on the held-out test set.

        Args:
            model: Trained model
            X_test: Test features (already preprocessed)
            y_test: Test labels
            feature_names: List of feature names
            class_names: Optional list of original class names
            threshold: Classification threshold (default 0.5, can be optimized for context)

        Returns:
            EvaluationResult with metrics
        """
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score,
            roc_auc_score, confusion_matrix, classification_report,
            mean_squared_error, mean_absolute_error, r2_score
        )
        from .evaluator import EvaluationMetrics, FeatureImportance, PerClassMetrics

        # Get probabilities for classification
        probabilities = None
        if not self.task_info.is_regression and hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(X_test)

        # Make predictions - use custom threshold for binary classification
        if (not self.task_info.is_regression and self.task_info.is_binary and
            probabilities is not None and threshold != 0.5):
            # Use optimized threshold
            predictions = (probabilities[:, 1] >= threshold).astype(int)
        else:
            predictions = model.predict(X_test)

        # Calculate metrics
        metrics = EvaluationMetrics()

        if self.task_info.is_regression:
            metrics.rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
            metrics.mae = float(mean_absolute_error(y_test, predictions))
            metrics.r2 = float(r2_score(y_test, predictions))
            # MAPE
            mask = y_test != 0
            if mask.sum() > 0:
                metrics.mape = float(np.mean(np.abs((y_test[mask] - predictions[mask]) / y_test[mask])) * 100)
            classification_report_str = None
        else:
            # Classification metrics
            average = 'binary' if self.task_info.is_binary else 'macro'
            metrics.accuracy = float(accuracy_score(y_test, predictions))
            metrics.precision = float(precision_score(y_test, predictions, average=average, zero_division=0))
            metrics.recall = float(recall_score(y_test, predictions, average=average, zero_division=0))
            metrics.f1 = float(f1_score(y_test, predictions, average=average, zero_division=0))
            metrics.confusion_matrix = confusion_matrix(y_test, predictions)

            # Per-class metrics
            try:
                classes = np.unique(y_test)
                per_class_prec = precision_score(y_test, predictions, average=None, zero_division=0)
                per_class_rec = recall_score(y_test, predictions, average=None, zero_division=0)
                per_class_f1 = f1_score(y_test, predictions, average=None, zero_division=0)

                metrics.per_class_metrics = []
                for i, cls in enumerate(classes):
                    support = int(np.sum(y_test == cls))
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
            if probabilities is not None:
                try:
                    if self.task_info.is_binary:
                        metrics.roc_auc = float(roc_auc_score(y_test, probabilities[:, 1]))
                    else:
                        metrics.roc_auc = float(roc_auc_score(
                            y_test, probabilities, multi_class='ovr', average='macro'
                        ))
                except Exception:
                    metrics.roc_auc = None

            classification_report_str = classification_report(y_test, predictions)

        # Get feature importance
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_importance = FeatureImportance(
                feature_names=list(feature_names),
                importances=list(importances),
                importance_type="model"
            )
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_)
            if len(importances.shape) > 1:
                importances = np.mean(importances, axis=0)
            feature_importance = FeatureImportance(
                feature_names=list(feature_names),
                importances=list(importances),
                importance_type="model"
            )

        return EvaluationResult(
            metrics=metrics,
            feature_importance=feature_importance,
            predictions=predictions,
            probabilities=probabilities,
            classification_report_str=classification_report_str
        )

    def _apply_production_features(
        self,
        model: Any,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        is_regression: bool
    ) -> None:
        """
        Apply production-grade features: calibration, confidence intervals, drift baseline.

        These features ensure the model is production-ready with:
        - Calibrated probability estimates
        - Statistical confidence in metrics
        - Baseline for drift monitoring
        - Uncertainty quantification

        Args:
            model: Trained model
            X_train: Training features
            y_train: Training targets
            X_test: Test features
            y_test: Test targets
            is_regression: Whether task is regression
        """
        task_type = "regression" if is_regression else "classification"

        # 1. Model Calibration (classification only)
        if self.calibrate_probabilities and not is_regression:
            if self.verbose:
                print("\n  Calibrating probability estimates...")
            try:
                # Split training data for calibration
                n_calib = min(int(len(X_train) * 0.2), 1000)
                if n_calib >= 50:
                    X_calib = X_train[-n_calib:]
                    y_calib = y_train[-n_calib:]

                    self.calibration_result = self.model_calibrator.calibrate(
                        model, X_train[:-n_calib], y_train[:-n_calib],
                        X_calib, y_calib
                    )

                    if self.verbose and self.calibration_result:
                        print(f"    Original ECE: {self.calibration_result.original_ece:.4f}")
                        print(f"    Calibrated ECE: {self.calibration_result.calibrated_ece:.4f}")
                        print(f"    Method: {self.calibration_result.method_used}")
                        if self.calibration_result.calibrated_ece < self.calibration_result.original_ece:
                            print(f"    Improvement: {(1 - self.calibration_result.calibrated_ece/self.calibration_result.original_ece)*100:.1f}%")
            except Exception as e:
                if self.verbose:
                    print(f"    Calibration skipped: {e}")

        # 2. Confidence Intervals for Metrics
        if self.compute_confidence_intervals:
            if self.verbose:
                print("\n  Computing confidence intervals (bootstrap)...")
            try:
                if is_regression:
                    ci_estimator = RegressionMetricsCI(n_bootstrap=500, confidence_level=0.95)
                    predictions = model.predict(X_test)
                    self.confidence_intervals = ci_estimator.compute_all(y_test, predictions)
                else:
                    ci_estimator = ClassificationMetricsCI(n_bootstrap=500, confidence_level=0.95)
                    predictions = model.predict(X_test)
                    probas = None
                    if hasattr(model, 'predict_proba'):
                        probas = model.predict_proba(X_test)
                    self.confidence_intervals = ci_estimator.compute_all(
                        y_test, predictions, probas
                    )

                if self.verbose and self.confidence_intervals:
                    print("    95% Confidence Intervals:")
                    for metric_name, ci in list(self.confidence_intervals.items())[:4]:
                        print(f"      {metric_name}: [{ci.lower:.4f}, {ci.upper:.4f}]")
            except Exception as e:
                if self.verbose:
                    print(f"    CI computation skipped: {e}")

        # 3. Drift Detection Baseline
        if self.save_drift_baseline:
            if self.verbose:
                print("\n  Saving drift detection baseline...")
            try:
                # Store training data distributions as reference
                self.drift_baseline = self.drift_detector.compute_baseline(
                    X_train, feature_names=None
                )

                if self.verbose and self.drift_baseline:
                    print(f"    Baseline saved for {self.drift_baseline.n_features} features")
                    print("    Use drift_detector.detect_drift(new_data) for monitoring")
            except Exception as e:
                if self.verbose:
                    print(f"    Drift baseline skipped: {e}")

        # 4. Uncertainty Quantification Setup
        try:
            # Calibrate uncertainty quantifier for future predictions
            # Use a subset of training data for calibration
            n_uncert_calib = min(int(len(X_train) * 0.15), 500)
            if n_uncert_calib >= 30:
                self.uncertainty_quantifier.calibrate(
                    model,
                    X_train[-n_uncert_calib:],
                    y_train[-n_uncert_calib:],
                    task_type=task_type
                )

                # Generate uncertainty report on test set
                self.uncertainty_report = self.uncertainty_quantifier.quantify(
                    model, X_test, y_test
                )

                if self.verbose and self.uncertainty_report:
                    if is_regression:
                        print(f"\n  Uncertainty: Mean interval width: {self.uncertainty_report.mean_interval_width:.4f}")
                        if self.uncertainty_report.empirical_coverage:
                            print(f"    Empirical coverage: {self.uncertainty_report.empirical_coverage:.1%}")
                    else:
                        high_uncert = self.uncertainty_report.get_high_uncertainty_indices(0.5)
                        print(f"\n  Uncertainty: {len(high_uncert)} samples with high uncertainty ({len(high_uncert)/len(X_test)*100:.1f}%)")
        except Exception as e:
            if self.verbose:
                print(f"    Uncertainty quantification skipped: {e}")

        # 5. Ensemble Building (optional)
        if self.enable_ensemble and hasattr(self, 'training_report') and self.training_report:
            if self.verbose:
                print("\n  Building model ensemble...")
            try:
                # Get all trained models from the training report
                models_for_ensemble = []
                for result in self.training_report.model_results[:5]:  # Top 5 models
                    if hasattr(result.model, 'predict'):
                        models_for_ensemble.append((result.name, result.model))

                if len(models_for_ensemble) >= 2:
                    # Map string to EnsembleMethod
                    method_map = {
                        'averaging': EnsembleMethod.AVERAGING,
                        'weighted': EnsembleMethod.WEIGHTED,
                        'stacking': EnsembleMethod.STACKING,
                        'voting': EnsembleMethod.VOTING
                    }
                    ensemble_method = method_map.get(self.ensemble_method, EnsembleMethod.WEIGHTED)

                    builder = EnsembleBuilder(task_type=task_type, method=ensemble_method)

                    # Get scores for weighting
                    scores = {r.name: r.cv_score for r in self.training_report.model_results[:5]}

                    ensemble = builder.build(
                        models_for_ensemble,
                        X_train, y_train,
                        X_test, y_test,
                        scores=scores
                    )

                    # Analyze ensemble
                    self.ensemble_metrics = builder.analyze_ensemble(X_test, y_test)

                    if self.verbose and self.ensemble_metrics:
                        print(f"    Ensemble score: {self.ensemble_metrics.ensemble_score:.4f}")
                        print(f"    Best individual: {max(self.ensemble_metrics.individual_scores.values()):.4f}")
                        print(f"    Improvement: {self.ensemble_metrics.improvement_over_best:+.4f}")
                        print(f"    Diversity: {self.ensemble_metrics.diversity_measure:.4f}")
            except Exception as e:
                if self.verbose:
                    print(f"    Ensemble building skipped: {e}")

    def _run_production_gates(
        self,
        df: pd.DataFrame,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> GateReport:
        """
        Run production readiness gates and return verdict.

        This evaluates whether the model is production-ready, experimental, or invalid.
        """
        # Build gate context from pipeline state
        context = GateContext()

        # Dataset info
        context.df = df
        context.n_rows = len(df)
        context.n_features = len(df.columns) - 1
        context.target_column = self.profile.target_column

        # Target analysis
        context.is_classification = not self.task_info.is_regression
        context.is_binary = self.task_info.is_binary if hasattr(self.task_info, 'is_binary') else True

        # Get n_classes from task_info, class_distribution, or target_unique_values
        if hasattr(self.task_info, 'n_classes') and self.task_info.n_classes is not None:
            context.n_classes = self.task_info.n_classes
        elif self.profile.class_distribution:
            context.n_classes = len(self.profile.class_distribution)
        elif hasattr(self.profile, 'target_unique_values') and self.profile.target_unique_values is not None:
            context.n_classes = self.profile.target_unique_values
        else:
            context.n_classes = 2  # Default for binary classification

        if self.profile.class_distribution:
            context.class_distribution = self.profile.class_distribution
            total = sum(self.profile.class_distribution.values())
            if total > 0:
                context.majority_class_ratio = max(self.profile.class_distribution.values()) / total

        # Model info
        context.model_name = self.training_report.best_model_name
        context.cv_scores = list(self.training_report.best_cv_scores) if hasattr(self.training_report, 'best_cv_scores') else []
        context.cv_mean = self.training_report.best_score
        context.cv_std = self.training_report.best_std if hasattr(self.training_report, 'best_std') else 0.0
        context.test_score = self.evaluation_result.metrics.f1 or self.evaluation_result.metrics.r2 or 0.0

        # Calculate baseline score (majority class accuracy for classification)
        if context.is_classification and context.class_distribution:
            total = sum(context.class_distribution.values())
            context.baseline_score = max(context.class_distribution.values()) / total if total > 0 else 0.5

        # Metrics
        metrics = self.evaluation_result.metrics
        context.accuracy = metrics.accuracy
        context.precision = metrics.precision
        context.recall = metrics.recall
        context.f1 = metrics.f1
        context.roc_auc = metrics.roc_auc
        context.r2 = metrics.r2
        context.rmse = metrics.rmse
        context.mae = metrics.mae

        # Feature analysis
        if self.evaluation_result.feature_importance:
            fi = self.evaluation_result.feature_importance
            context.feature_importance = dict(zip(fi.feature_names, fi.importances))
            if fi.importances:
                total_imp = sum(fi.importances)
                if total_imp > 0:
                    context.top_feature_importance = max(fi.importances) / total_imp

        # Leakage info
        if self.leakage_report:
            context.has_leakage = self.leakage_report.has_high_risk
            context.leakage_warnings = [w.feature for w in self.leakage_report.warnings[:5]]

        # Data quality
        context.missing_ratio = self.profile.missing_ratio if hasattr(self.profile, 'missing_ratio') else 0.0

        # Find high missing and zero variance columns
        if hasattr(self.profile, 'missing_percentages'):
            context.high_missing_cols = [
                col for col, pct in self.profile.missing_percentages.items()
                if pct > 95
            ]

        # Run gates
        self.gate_report = self.gate_runner.run(context)

        return self.gate_report
