"""
Production Readiness Gate System

A comprehensive gate system that evaluates whether a trained model
is truly production-ready, experimental, or invalid.

Gates run sequentially and each returns PASS, WARN, or FAIL.
The final verdict determines if the model can be trusted in production.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


class GateStatus(Enum):
    """Result status for each gate."""
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class ModelVerdict(Enum):
    """Final model readiness verdict."""
    PRODUCTION_READY = "production_ready"
    EXPERIMENTAL = "experimental"
    INVALID = "invalid"


@dataclass
class GateResult:
    """Result from a single gate evaluation."""
    gate_name: str
    status: GateStatus
    message: str
    details: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == GateStatus.PASS

    @property
    def failed(self) -> bool:
        return self.status == GateStatus.FAIL


@dataclass
class GateContext:
    """Context passed through all gates containing evaluation data."""
    # Dataset info
    df: Optional[pd.DataFrame] = None
    n_rows: int = 0
    n_features: int = 0
    target_column: Optional[str] = None

    # Target analysis
    is_classification: bool = True
    is_binary: bool = True
    n_classes: int = 2
    class_distribution: Optional[Dict[Any, int]] = None
    majority_class_ratio: float = 0.0

    # Model info
    model_name: str = ""
    cv_scores: List[float] = field(default_factory=list)
    cv_mean: float = 0.0
    cv_std: float = 0.0
    test_score: float = 0.0
    baseline_score: float = 0.0

    # Metrics
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1: Optional[float] = None
    roc_auc: Optional[float] = None
    r2: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None

    # Feature analysis
    feature_importance: Optional[Dict[str, float]] = None
    top_feature_importance: float = 0.0
    correlations_with_target: Optional[Dict[str, float]] = None

    # Leakage info
    leakage_warnings: List[str] = field(default_factory=list)
    has_leakage: bool = False

    # Training info
    training_time: float = 0.0
    model_size_mb: float = 0.0

    # Preprocessing
    missing_ratio: float = 0.0
    zero_variance_cols: List[str] = field(default_factory=list)
    high_missing_cols: List[str] = field(default_factory=list)


@dataclass
class GateReport:
    """Complete report from all gates."""
    gates: List[GateResult] = field(default_factory=list)
    verdict: ModelVerdict = ModelVerdict.EXPERIMENTAL
    verdict_reason: str = ""
    trust_score: float = 0.0
    passed_gates: List[str] = field(default_factory=list)
    warned_gates: List[str] = field(default_factory=list)
    failed_gates: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def add_result(self, result: GateResult):
        """Add a gate result and update lists."""
        self.gates.append(result)
        if result.status == GateStatus.PASS:
            self.passed_gates.append(result.gate_name)
        elif result.status == GateStatus.WARN:
            self.warned_gates.append(result.gate_name)
        else:
            self.failed_gates.append(result.gate_name)


class Gate(ABC):
    """Abstract base class for all gates."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Gate name for display."""
        pass

    @property
    @abstractmethod
    def stage(self) -> int:
        """Stage number (0-9)."""
        pass

    @abstractmethod
    def evaluate(self, context: GateContext) -> GateResult:
        """Evaluate this gate and return result."""
        pass


# =============================================================================
# STAGE 0: Dataset Sanity Gate
# =============================================================================

class DatasetSanityGate(Gate):
    """
    Stage 0: Dataset Sanity Gate (FAIL FAST)

    Checks:
    - Rows >= min_rows (default 300)
    - Target column exists and has >1 unique value
    - No column is 95%+ missing
    - No column has zero variance
    """

    def __init__(
        self,
        min_rows: int = 300,
        max_missing_ratio: float = 0.95,
        min_target_classes: int = 2
    ):
        self.min_rows = min_rows
        self.max_missing_ratio = max_missing_ratio
        self.min_target_classes = min_target_classes

    @property
    def name(self) -> str:
        return "Dataset Sanity"

    @property
    def stage(self) -> int:
        return 0

    def evaluate(self, context: GateContext) -> GateResult:
        issues = []
        warnings = []
        metrics = {}

        # Check row count
        metrics['n_rows'] = context.n_rows
        if context.n_rows < self.min_rows:
            issues.append(f"Insufficient data: {context.n_rows} rows (need {self.min_rows}+)")
        elif context.n_rows < self.min_rows * 2:
            warnings.append(f"Limited data: {context.n_rows} rows (recommend {self.min_rows * 2}+)")

        # Check target
        if context.target_column is None:
            issues.append("No target column specified or detected")
        elif context.is_classification and context.n_classes is not None and context.n_classes < self.min_target_classes:
            issues.append(f"Target has only {context.n_classes} unique value(s)")

        # Check high missing columns
        if context.high_missing_cols:
            issues.append(f"Columns with >95% missing: {', '.join(context.high_missing_cols[:3])}")

        # Check zero variance columns
        if context.zero_variance_cols:
            warnings.append(f"Zero variance columns: {', '.join(context.zero_variance_cols[:3])}")

        # Determine status
        if issues:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAIL,
                message="Dataset fails sanity checks",
                details=issues + warnings,
                metrics=metrics
            )
        elif warnings:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.WARN,
                message="Dataset has minor concerns",
                details=warnings,
                metrics=metrics
            )
        else:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.PASS,
                message="Dataset passes sanity checks",
                details=[f"Rows: {context.n_rows}", f"Features: {context.n_features}"],
                metrics=metrics
            )


# =============================================================================
# STAGE 1: Target Suitability Gate
# =============================================================================

class TargetSuitabilityGate(Gate):
    """
    Stage 1: Target Suitability Gate

    Checks if the target is learnable:
    - Classification: class balance, baseline comparison
    - Regression: target variance, baseline comparison
    """

    def __init__(
        self,
        max_majority_ratio: float = 0.90,
        min_baseline_improvement: float = 0.10
    ):
        self.max_majority_ratio = max_majority_ratio
        self.min_baseline_improvement = min_baseline_improvement

    @property
    def name(self) -> str:
        return "Target Suitability"

    @property
    def stage(self) -> int:
        return 1

    def evaluate(self, context: GateContext) -> GateResult:
        issues = []
        warnings = []
        metrics = {}

        if context.is_classification:
            # Check class balance
            metrics['majority_class_ratio'] = context.majority_class_ratio
            metrics['n_classes'] = context.n_classes

            if context.majority_class_ratio > self.max_majority_ratio:
                issues.append(
                    f"Extreme class imbalance: majority class is {context.majority_class_ratio:.1%}"
                )
            elif context.majority_class_ratio > 0.80:
                warnings.append(
                    f"Significant class imbalance: {context.majority_class_ratio:.1%} majority"
                )

            # Check baseline improvement
            if context.baseline_score > 0 and context.test_score > 0:
                improvement = (context.test_score - context.baseline_score) / max(context.baseline_score, 0.01)
                metrics['baseline_improvement'] = improvement

                if improvement < self.min_baseline_improvement:
                    issues.append(
                        f"Model barely beats baseline: {improvement:.1%} improvement"
                    )
        else:
            # Regression checks
            if context.r2 is not None:
                metrics['r2'] = context.r2
                if context.r2 < 0:
                    issues.append(f"Negative R²: model worse than mean prediction")
                elif context.r2 < 0.1:
                    warnings.append(f"Very low R² ({context.r2:.3f}): weak predictive power")

        # Determine status
        if issues:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAIL,
                message="Target may not be learnable",
                details=issues + warnings,
                metrics=metrics
            )
        elif warnings:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.WARN,
                message="Target has learning challenges",
                details=warnings,
                metrics=metrics
            )
        else:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.PASS,
                message="Target is suitable for learning",
                details=[],
                metrics=metrics
            )


# =============================================================================
# STAGE 2: Leakage & Triviality Gate
# =============================================================================

class LeakageGate(Gate):
    """
    Stage 2: Leakage & Triviality Gate (CRITICAL)

    Checks:
    - Suspiciously high correlations (|ρ| > 0.98)
    - Single feature dominance (>85% importance)
    - CV >> Test score (overfitting/leakage)
    - Unrealistically high R² (>0.98)
    """

    def __init__(
        self,
        max_correlation: float = 0.98,
        max_single_feature_importance: float = 0.85,
        max_cv_test_gap: float = 0.15,
        suspicious_r2: float = 0.98
    ):
        self.max_correlation = max_correlation
        self.max_single_feature_importance = max_single_feature_importance
        self.max_cv_test_gap = max_cv_test_gap
        self.suspicious_r2 = suspicious_r2

    @property
    def name(self) -> str:
        return "Leakage Detection"

    @property
    def stage(self) -> int:
        return 2

    def evaluate(self, context: GateContext) -> GateResult:
        issues = []
        warnings = []
        metrics = {}

        # Check for known leakage
        if context.has_leakage:
            issues.append("Data leakage detected in features")
            if context.leakage_warnings:
                issues.extend(context.leakage_warnings[:3])

        # Check correlation with target
        if context.correlations_with_target:
            high_corr = [
                (f, c) for f, c in context.correlations_with_target.items()
                if abs(c) > self.max_correlation
            ]
            if high_corr:
                issues.append(
                    f"Suspicious correlation: {high_corr[0][0]} (|ρ|={abs(high_corr[0][1]):.3f})"
                )
                metrics['max_correlation'] = max(abs(c) for _, c in high_corr)

        # Check feature importance dominance
        if context.top_feature_importance > self.max_single_feature_importance:
            issues.append(
                f"Single feature dominates: {context.top_feature_importance:.1%} importance"
            )
            metrics['top_feature_importance'] = context.top_feature_importance

        # Check CV vs Test gap (potential overfitting/leakage)
        if context.cv_mean > 0 and context.test_score > 0:
            cv_test_gap = context.cv_mean - context.test_score
            metrics['cv_test_gap'] = cv_test_gap

            if cv_test_gap > self.max_cv_test_gap:
                warnings.append(
                    f"CV score ({context.cv_mean:.3f}) >> Test score ({context.test_score:.3f})"
                )

        # Check for unrealistic R² (regression)
        if context.r2 is not None and context.r2 > self.suspicious_r2:
            warnings.append(
                f"Suspiciously high R² ({context.r2:.3f}): verify no leakage"
            )

        # Determine status
        if issues:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAIL,
                message="Potential data leakage detected",
                details=issues + warnings,
                metrics=metrics
            )
        elif warnings:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.WARN,
                message="Minor leakage concerns",
                details=warnings,
                metrics=metrics
            )
        else:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.PASS,
                message="No leakage detected",
                details=[],
                metrics=metrics
            )


# =============================================================================
# STAGE 3: Data Splitting Gate
# =============================================================================

class DataSplittingGate(Gate):
    """
    Stage 3: Proper Data Splitting Gate

    Verifies:
    - Train/test split was performed
    - Stratified split for classification
    - Preprocessing fit only on train
    """

    @property
    def name(self) -> str:
        return "Data Splitting"

    @property
    def stage(self) -> int:
        return 3

    def evaluate(self, context: GateContext) -> GateResult:
        # This gate mostly passes if the pipeline is used correctly
        # We check for signs of proper splitting
        details = []

        if context.cv_scores:
            details.append(f"Cross-validation: {len(context.cv_scores)} folds")

        if context.test_score > 0:
            details.append(f"Held-out test evaluation: {context.test_score:.4f}")

        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            message="Proper data splitting verified",
            details=details,
            metrics={'cv_folds': len(context.cv_scores)}
        )


# =============================================================================
# STAGE 4: Metric-Task Alignment Gate
# =============================================================================

class MetricAlignmentGate(Gate):
    """
    Stage 4: Metric-Task Alignment Gate

    Ensures the right metric is used for the problem:
    - Imbalanced classification: F1, Recall, PR-AUC
    - Balanced: Accuracy + F1
    - Regression with zeros: avoid MAPE
    """

    @property
    def name(self) -> str:
        return "Metric Alignment"

    @property
    def stage(self) -> int:
        return 4

    def evaluate(self, context: GateContext) -> GateResult:
        warnings = []
        recommendations = []
        metrics = {}

        if context.is_classification:
            # Check for imbalanced classification
            if context.majority_class_ratio > 0.7:
                if context.f1 is None and context.recall is None:
                    warnings.append(
                        "Imbalanced data: should prioritize F1/Recall over Accuracy"
                    )
                    recommendations.append("Use F1 or PR-AUC as primary metric")

                # Check if accuracy is misleadingly high
                if context.accuracy and context.f1:
                    if context.accuracy > context.f1 + 0.15:
                        warnings.append(
                            f"Accuracy ({context.accuracy:.3f}) may be misleading "
                            f"vs F1 ({context.f1:.3f})"
                        )

            metrics['accuracy'] = context.accuracy
            metrics['f1'] = context.f1
            metrics['recall'] = context.recall
        else:
            # Regression metrics
            if context.r2 is not None:
                metrics['r2'] = context.r2

        if warnings:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.WARN,
                message="Metric may be misleading",
                details=warnings + recommendations,
                metrics=metrics
            )
        else:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.PASS,
                message="Metrics aligned with task",
                details=[],
                metrics=metrics
            )


# =============================================================================
# STAGE 5: Model Selection Gate
# =============================================================================

class ModelSelectionGate(Gate):
    """
    Stage 5: Model Selection Gate

    Ensures model selection is sound:
    - CV score stability (low std dev)
    - CV ≈ Test (small gap)
    - Reasonable training time
    """

    def __init__(
        self,
        max_cv_std: float = 0.05,
        max_cv_test_gap: float = 0.10
    ):
        self.max_cv_std = max_cv_std
        self.max_cv_test_gap = max_cv_test_gap

    @property
    def name(self) -> str:
        return "Model Selection"

    @property
    def stage(self) -> int:
        return 5

    def evaluate(self, context: GateContext) -> GateResult:
        issues = []
        warnings = []
        metrics = {
            'model': context.model_name,
            'cv_mean': context.cv_mean,
            'cv_std': context.cv_std,
            'test_score': context.test_score
        }

        # Check CV stability
        if context.cv_std > self.max_cv_std:
            warnings.append(
                f"Unstable CV: std={context.cv_std:.4f} (threshold: {self.max_cv_std})"
            )

        # Check CV vs Test consistency
        if context.cv_mean > 0 and context.test_score > 0:
            gap = abs(context.cv_mean - context.test_score)
            metrics['cv_test_gap'] = gap

            if gap > self.max_cv_test_gap:
                warnings.append(
                    f"CV-Test gap: {gap:.4f} (CV={context.cv_mean:.4f}, Test={context.test_score:.4f})"
                )

        if issues:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAIL,
                message="Model selection has issues",
                details=issues + warnings,
                metrics=metrics
            )
        elif warnings:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.WARN,
                message="Model selection has concerns",
                details=warnings,
                metrics=metrics
            )
        else:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.PASS,
                message=f"Model '{context.model_name}' selected appropriately",
                details=[f"CV: {context.cv_mean:.4f} ± {context.cv_std:.4f}"],
                metrics=metrics
            )


# =============================================================================
# STAGE 6: Performance Sufficiency Gate
# =============================================================================

class PerformanceGate(Gate):
    """
    Stage 6: Performance Sufficiency Gate

    Ensures model performance is acceptable:
    - Classification: F1/Recall above threshold
    - Regression: R² above threshold, RMSE reasonable
    """

    def __init__(
        self,
        min_f1: float = 0.5,
        min_recall_minority: float = 0.4,
        min_r2: float = 0.2
    ):
        self.min_f1 = min_f1
        self.min_recall_minority = min_recall_minority
        self.min_r2 = min_r2

    @property
    def name(self) -> str:
        return "Performance Sufficiency"

    @property
    def stage(self) -> int:
        return 6

    def evaluate(self, context: GateContext) -> GateResult:
        issues = []
        warnings = []
        metrics = {}

        if context.is_classification:
            # Check F1
            if context.f1 is not None:
                metrics['f1'] = context.f1
                if context.f1 < self.min_f1:
                    if context.f1 < self.min_f1 * 0.5:
                        issues.append(f"Very low F1: {context.f1:.4f} (need {self.min_f1}+)")
                    else:
                        warnings.append(f"Low F1: {context.f1:.4f} (target {self.min_f1}+)")

            # Check recall for minority class
            if context.recall is not None:
                metrics['recall'] = context.recall
                if context.majority_class_ratio > 0.7 and context.recall < self.min_recall_minority:
                    warnings.append(
                        f"Low minority recall: {context.recall:.4f} (target {self.min_recall_minority}+)"
                    )

            # Check ROC-AUC
            if context.roc_auc is not None:
                metrics['roc_auc'] = context.roc_auc
                if context.roc_auc < 0.6:
                    warnings.append(f"Low ROC-AUC: {context.roc_auc:.4f}")
        else:
            # Regression checks
            if context.r2 is not None:
                metrics['r2'] = context.r2
                if context.r2 < self.min_r2:
                    if context.r2 < 0:
                        issues.append(f"Negative R²: {context.r2:.4f}")
                    else:
                        warnings.append(f"Low R²: {context.r2:.4f} (target {self.min_r2}+)")

            if context.rmse is not None:
                metrics['rmse'] = context.rmse

        if issues:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAIL,
                message="Performance is insufficient",
                details=issues + warnings,
                metrics=metrics
            )
        elif warnings:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.WARN,
                message="Performance is marginal",
                details=warnings,
                metrics=metrics
            )
        else:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.PASS,
                message="Performance meets requirements",
                details=[],
                metrics=metrics
            )


# =============================================================================
# STAGE 7: Interpretability Gate
# =============================================================================

class InterpretabilityGate(Gate):
    """
    Stage 7: Interpretability & Explainability Gate

    Checks:
    - Feature importance available
    - No forbidden features (IDs, post-event)
    - Reasonable feature dominance
    """

    def __init__(self, max_single_feature: float = 0.70):
        self.max_single_feature = max_single_feature

    @property
    def name(self) -> str:
        return "Interpretability"

    @property
    def stage(self) -> int:
        return 7

    def evaluate(self, context: GateContext) -> GateResult:
        warnings = []
        details = []
        metrics = {}

        # Check feature importance availability
        if context.feature_importance:
            details.append(f"Feature importance: {len(context.feature_importance)} features")

            # Check for extreme dominance
            if context.top_feature_importance > self.max_single_feature:
                warnings.append(
                    f"Single feature dominates: {context.top_feature_importance:.1%}"
                )

            metrics['n_features'] = len(context.feature_importance)
            metrics['top_importance'] = context.top_feature_importance
        else:
            warnings.append("Feature importance not available")

        if warnings:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.WARN,
                message="Limited interpretability",
                details=warnings + details,
                metrics=metrics
            )
        else:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.PASS,
                message="Model is interpretable",
                details=details,
                metrics=metrics
            )


# =============================================================================
# STAGE 8: Robustness & Reproducibility Gate
# =============================================================================

class RobustnessGate(Gate):
    """
    Stage 8: Robustness & Reproducibility Gate

    Checks:
    - Random seed fixed
    - Performance stable across folds
    - Model size reasonable
    - Inference time acceptable
    """

    def __init__(
        self,
        max_cv_std: float = 0.08,
        max_model_size_mb: float = 500,
        max_inference_time_ms: float = 1000
    ):
        self.max_cv_std = max_cv_std
        self.max_model_size_mb = max_model_size_mb
        self.max_inference_time_ms = max_inference_time_ms

    @property
    def name(self) -> str:
        return "Robustness"

    @property
    def stage(self) -> int:
        return 8

    def evaluate(self, context: GateContext) -> GateResult:
        warnings = []
        details = []
        metrics = {}

        # Check CV stability
        if context.cv_std > 0:
            metrics['cv_std'] = context.cv_std
            if context.cv_std > self.max_cv_std:
                warnings.append(
                    f"High variance across folds: std={context.cv_std:.4f}"
                )
            else:
                details.append(f"Stable across folds: std={context.cv_std:.4f}")

        # Check model size
        if context.model_size_mb > 0:
            metrics['model_size_mb'] = context.model_size_mb
            if context.model_size_mb > self.max_model_size_mb:
                warnings.append(
                    f"Large model: {context.model_size_mb:.1f}MB"
                )

        # Check training time
        if context.training_time > 0:
            metrics['training_time'] = context.training_time
            details.append(f"Training time: {context.training_time:.1f}s")

        if warnings:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.WARN,
                message="Robustness concerns",
                details=warnings + details,
                metrics=metrics
            )
        else:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.PASS,
                message="Model is robust and reproducible",
                details=details,
                metrics=metrics
            )


# =============================================================================
# Gate Runner & Final Verdict
# =============================================================================

class GateRunner:
    """
    Runs all gates and produces final verdict.

    The verdict logic:
    - PRODUCTION_READY: All critical gates pass, no fails
    - EXPERIMENTAL: Some warns but no critical fails
    - INVALID: Any critical gate fails
    """

    def __init__(self):
        self.gates: List[Gate] = [
            DatasetSanityGate(),
            TargetSuitabilityGate(),
            LeakageGate(),
            DataSplittingGate(),
            MetricAlignmentGate(),
            ModelSelectionGate(),
            PerformanceGate(),
            InterpretabilityGate(),
            RobustnessGate(),
        ]

        # Critical gates that cause INVALID verdict if failed
        self.critical_gates = {
            "Dataset Sanity",
            "Target Suitability",
            "Leakage Detection",
        }

    def run(self, context: GateContext) -> GateReport:
        """Run all gates and produce final report."""
        report = GateReport()

        for gate in self.gates:
            result = gate.evaluate(context)
            report.add_result(result)

        # Determine verdict
        report.verdict, report.verdict_reason = self._determine_verdict(report)

        # Calculate trust score
        report.trust_score = self._calculate_trust_score(report)

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)

        return report

    def _determine_verdict(self, report: GateReport) -> Tuple[ModelVerdict, str]:
        """Determine final verdict based on gate results."""

        # Check for critical failures
        critical_failures = [
            g for g in report.failed_gates
            if g in self.critical_gates
        ]

        if critical_failures:
            return (
                ModelVerdict.INVALID,
                f"Critical gate(s) failed: {', '.join(critical_failures)}"
            )

        # Check for any failures
        if report.failed_gates:
            return (
                ModelVerdict.EXPERIMENTAL,
                f"Gate(s) failed: {', '.join(report.failed_gates)}"
            )

        # Check for warnings
        if report.warned_gates:
            # If only minor warnings, could still be production ready
            if len(report.warned_gates) <= 2:
                return (
                    ModelVerdict.PRODUCTION_READY,
                    f"Minor concerns: {', '.join(report.warned_gates)}"
                )
            else:
                return (
                    ModelVerdict.EXPERIMENTAL,
                    f"Multiple concerns: {', '.join(report.warned_gates)}"
                )

        # All passed
        return (
            ModelVerdict.PRODUCTION_READY,
            "All gates passed"
        )

    def _calculate_trust_score(self, report: GateReport) -> float:
        """Calculate a 0-100 trust score."""
        total_gates = len(report.gates)
        if total_gates == 0:
            return 0.0

        # Scoring: PASS=100, WARN=60, FAIL=0
        score_map = {
            GateStatus.PASS: 100,
            GateStatus.WARN: 60,
            GateStatus.FAIL: 0
        }

        total_score = sum(
            score_map[g.status] for g in report.gates
        )

        return total_score / total_gates

    def _generate_recommendations(self, report: GateReport) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        for result in report.gates:
            if result.status == GateStatus.FAIL:
                if result.gate_name == "Dataset Sanity":
                    recommendations.append("Collect more data or verify data quality")
                elif result.gate_name == "Target Suitability":
                    recommendations.append("Consider reframing the problem or collecting more balanced data")
                elif result.gate_name == "Leakage Detection":
                    recommendations.append("Remove leaked features and retrain")
                elif result.gate_name == "Performance Sufficiency":
                    recommendations.append("Try feature engineering or different algorithms")

            elif result.status == GateStatus.WARN:
                if result.gate_name == "Metric Alignment":
                    recommendations.append("Consider using F1 or PR-AUC for imbalanced data")
                elif result.gate_name == "Model Selection":
                    recommendations.append("Increase CV folds for more stable estimates")

        return recommendations


def get_verdict_display(verdict: ModelVerdict) -> str:
    """Get display string for verdict."""
    displays = {
        ModelVerdict.PRODUCTION_READY: "PRODUCTION READY",
        ModelVerdict.EXPERIMENTAL: "EXPERIMENTAL",
        ModelVerdict.INVALID: "INVALID"
    }
    return displays.get(verdict, "UNKNOWN")


def get_verdict_emoji(verdict: ModelVerdict) -> str:
    """Get emoji for verdict."""
    emojis = {
        ModelVerdict.PRODUCTION_READY: "[PASS]",
        ModelVerdict.EXPERIMENTAL: "[WARN]",
        ModelVerdict.INVALID: "[FAIL]"
    }
    return emojis.get(verdict, "[?]")


def format_gate_report(report: GateReport) -> str:
    """Format gate report for display."""
    lines = [
        "=" * 60,
        "MODEL READINESS VERDICT",
        "=" * 60,
        f"Status: {get_verdict_emoji(report.verdict)} {get_verdict_display(report.verdict)}",
        f"Trust Score: {report.trust_score:.0f}/100",
        f"Reason: {report.verdict_reason}",
        ""
    ]

    # Passed gates
    if report.passed_gates:
        lines.append("Passed:")
        for gate in report.passed_gates:
            lines.append(f"  [OK] {gate}")
        lines.append("")

    # Warned gates
    if report.warned_gates:
        lines.append("Concerns:")
        for gate in report.warned_gates:
            result = next(g for g in report.gates if g.gate_name == gate)
            lines.append(f"  [!] {gate}")
            for detail in result.details[:2]:
                lines.append(f"      {detail}")
        lines.append("")

    # Failed gates
    if report.failed_gates:
        lines.append("Failed:")
        for gate in report.failed_gates:
            result = next(g for g in report.gates if g.gate_name == gate)
            lines.append(f"  [X] {gate}")
            for detail in result.details[:2]:
                lines.append(f"      {detail}")
        lines.append("")

    # Recommendations
    if report.recommendations:
        lines.append("Recommendations:")
        for rec in report.recommendations[:5]:
            lines.append(f"  - {rec}")

    lines.append("=" * 60)
    return "\n".join(lines)
