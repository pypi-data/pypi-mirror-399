"""
TabuLaML - Fast, Explainable, No-Code AutoML for Tabular Data

A production-ready AutoML system that:
- Accepts CSV datasets
- Automatically determines the ML task (classification/regression)
- Preprocesses data (imputation, scaling, encoding)
- Trains multiple models (Logistic Regression, Random Forest, XGBoost, LightGBM)
- Selects the best-performing model using cross-validation
- Exports trained models (.pkl) and reports (HTML/JSON)

Usage:
    from automl import AutoMLPipeline

    pipeline = AutoMLPipeline()
    results = pipeline.run("data.csv", target_column="target")

CLI Usage:
    tabulaml train data.csv
    tabulaml train data.csv --target label
    tabulaml predict model.pkl new_data.csv
"""

from .pipeline import AutoMLPipeline
from .profiler import DataProfiler, DataProfile
from .task_inference import TaskInferrer, TaskInfo, TaskType
from .preprocessing import DataPreprocessor
from .balancer import DataBalancer, BalancingResult
from .models import ModelFactory, ModelCandidate
from .trainer import ModelTrainer, TrainingReport
from .evaluator import ModelEvaluator, EvaluationResult
from .exporter import ModelExporter
from .business_context import BusinessContextEvaluator, BusinessContext, BusinessInsight
from .leakage_detector import LeakageDetector, LeakageReport, LeakageWarning, LeakageRisk
from .readiness_scorer import ReadinessScorer, ReadinessScore, ReadinessLevel

# Production-grade features
from .calibration import ModelCalibrator, CalibrationResult, PlattScaler, IsotonicCalibrator
from .statistical_inference import (
    BootstrapEstimator, ClassificationMetricsCI, RegressionMetricsCI,
    ConfidenceInterval, ModelComparator
)
from .drift_detection import DriftDetector, DriftReport, PSICalculator, FeatureDriftResult
from .uncertainty import (
    UncertaintyQuantifier, UncertaintyReport, ConformalPredictor,
    PredictionInterval, ClassificationUncertainty
)
from .ensemble import (
    EnsembleBuilder, EnsembleMethod, EnsembleMetrics,
    AveragingEnsemble, WeightedEnsemble, StackingEnsemble, VotingEnsemble
)
from .gates import (
    GateRunner, GateContext, GateReport, GateResult,
    GateStatus, ModelVerdict, format_gate_report
)

__version__ = "0.1.1"
__author__ = "Sekpey Herbert"
__email__ = "sekepyherbert@gmail.com"

__all__ = [
    # Core pipeline
    "AutoMLPipeline",
    "DataProfiler",
    "DataProfile",
    "TaskInferrer",
    "TaskInfo",
    "TaskType",
    "DataPreprocessor",
    "DataBalancer",
    "BalancingResult",
    "ModelFactory",
    "ModelCandidate",
    "ModelTrainer",
    "TrainingReport",
    "ModelEvaluator",
    "EvaluationResult",
    "ModelExporter",
    # Business context
    "BusinessContextEvaluator",
    "BusinessContext",
    "BusinessInsight",
    # Leakage detection
    "LeakageDetector",
    "LeakageReport",
    "LeakageWarning",
    "LeakageRisk",
    # Readiness scoring
    "ReadinessScorer",
    "ReadinessScore",
    "ReadinessLevel",
    # Calibration
    "ModelCalibrator",
    "CalibrationResult",
    "PlattScaler",
    "IsotonicCalibrator",
    # Statistical inference
    "BootstrapEstimator",
    "ClassificationMetricsCI",
    "RegressionMetricsCI",
    "ConfidenceInterval",
    "ModelComparator",
    # Drift detection
    "DriftDetector",
    "DriftReport",
    "PSICalculator",
    "FeatureDriftResult",
    # Uncertainty quantification
    "UncertaintyQuantifier",
    "UncertaintyReport",
    "ConformalPredictor",
    "PredictionInterval",
    "ClassificationUncertainty",
    # Ensemble methods
    "EnsembleBuilder",
    "EnsembleMethod",
    "EnsembleMetrics",
    "AveragingEnsemble",
    "WeightedEnsemble",
    "StackingEnsemble",
    "VotingEnsemble",
    # Production gates
    "GateRunner",
    "GateContext",
    "GateReport",
    "GateResult",
    "GateStatus",
    "ModelVerdict",
    "format_gate_report",
]
