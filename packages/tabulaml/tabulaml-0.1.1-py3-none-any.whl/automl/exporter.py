"""
Exporter Module

Handles model and report export:
- Trained model file (.pkl)
- Training report (JSON / Markdown / HTML)
- Model ranking and metrics
- Feature importance
- Evaluation artifacts (confusion matrix, error plots)
"""

import os
import json
import joblib
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

from .profiler import DataProfile
from .task_inference import TaskInfo, TaskType
from .trainer import TrainingReport
from .evaluator import EvaluationResult, EvaluationMetrics, PerClassMetrics


@dataclass
class ExportPaths:
    """Container for export file paths."""
    model_path: str
    report_json_path: str
    report_html_path: str
    confusion_matrix_path: Optional[str] = None
    feature_importance_path: Optional[str] = None
    residual_plot_path: Optional[str] = None


class ModelExporter:
    """Exports trained models, reports, and artifacts."""

    def __init__(self, output_dir: str = "outputs"):
        """
        Initialize the exporter.

        Args:
            output_dir: Base directory for outputs
        """
        self.output_dir = Path(output_dir)
        self.models_dir = self.output_dir / "models"
        self.reports_dir = self.output_dir / "reports"
        self.artifacts_dir = self.output_dir / "artifacts"

        # Create directories
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def export_all(
        self,
        model: Any,
        preprocessor: Any,
        profile: DataProfile,
        task_info: TaskInfo,
        training_report: TrainingReport,
        evaluation_result: EvaluationResult,
        run_name: Optional[str] = None
    ) -> ExportPaths:
        """
        Export model, preprocessor, and all reports.

        Args:
            model: Trained model
            preprocessor: Fitted preprocessor
            profile: DataProfile
            task_info: TaskInfo
            training_report: TrainingReport
            evaluation_result: EvaluationResult
            run_name: Optional name for this run

        Returns:
            ExportPaths with all file paths
        """
        # Generate run name
        if run_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            run_name = f"automl_{timestamp}"

        # Export model
        model_path = self.export_model(model, preprocessor, run_name)

        # Export reports
        report_data = self._build_report_data(
            profile, task_info, training_report, evaluation_result
        )
        report_json_path = self.export_json_report(report_data, run_name)
        report_html_path = self.export_html_report(report_data, run_name)

        # Export artifacts
        paths = ExportPaths(
            model_path=str(model_path),
            report_json_path=str(report_json_path),
            report_html_path=str(report_html_path)
        )

        # Confusion matrix for classification
        if not task_info.is_regression and evaluation_result.metrics.confusion_matrix is not None:
            cm_path = self.export_confusion_matrix(
                evaluation_result.metrics.confusion_matrix,
                run_name
            )
            paths.confusion_matrix_path = str(cm_path)

        # Feature importance
        if evaluation_result.feature_importance is not None:
            fi_path = self.export_feature_importance(
                evaluation_result.feature_importance.feature_names,
                evaluation_result.feature_importance.importances,
                run_name
            )
            paths.feature_importance_path = str(fi_path)

        return paths

    def export_model(
        self,
        model: Any,
        preprocessor: Any,
        run_name: str
    ) -> Path:
        """
        Export model and preprocessor to .pkl file.

        Args:
            model: Trained model
            preprocessor: Fitted preprocessor
            run_name: Name for this run

        Returns:
            Path to saved model file
        """
        model_path = self.models_dir / f"{run_name}_model.pkl"

        # Save as a dictionary containing both model and preprocessor
        model_bundle = {
            'model': model,
            'preprocessor': preprocessor,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }

        joblib.dump(model_bundle, model_path)

        return model_path

    def _get_metric_description(self, scoring_metric: str, task_info: TaskInfo) -> str:
        """Get human-readable description of the scoring metric."""
        descriptions = {
            'roc_auc': 'ROC-AUC (Area Under ROC Curve) - measures ability to distinguish between classes. Range: 0.5 (random) to 1.0 (perfect).',
            'f1_macro': 'F1-Macro (macro-averaged F1 score) - harmonic mean of precision and recall, averaged across all classes. Range: 0.0 to 1.0.',
            'neg_root_mean_squared_error': 'Negative RMSE (Root Mean Squared Error) - average prediction error magnitude. More negative = worse. Closer to 0 = better.'
        }
        return descriptions.get(scoring_metric, f'{scoring_metric} - model selection metric')

    def _build_report_data(
        self,
        profile: DataProfile,
        task_info: TaskInfo,
        training_report: TrainingReport,
        evaluation_result: EvaluationResult
    ) -> Dict[str, Any]:
        """Build a comprehensive report dictionary."""
        # Convert metrics to dict safely
        metrics_dict = {}
        if evaluation_result.metrics:
            m = evaluation_result.metrics
            metrics_dict = {
                'accuracy': m.accuracy,
                'precision': m.precision,
                'recall': m.recall,
                'f1': m.f1,
                'roc_auc': m.roc_auc,
                'rmse': m.rmse,
                'mae': m.mae,
                'r2': m.r2,
                'mape': m.mape
            }
            # Remove None values
            metrics_dict = {k: v for k, v in metrics_dict.items() if v is not None}

        # Build training results (CV scores)
        training_results = []
        for result in training_report.results:
            training_results.append({
                'model_name': result.model_name,
                'mean_score': result.mean_score,
                'std_score': result.std_score,
                'cv_scores': result.cv_scores,  # Include individual CV fold scores
                'training_time': result.training_time,
                'is_best': result.is_best
            })

        # Build feature importance
        feature_importance = None
        if evaluation_result.feature_importance:
            fi = evaluation_result.feature_importance
            feature_importance = [
                {'feature': name, 'importance': imp}
                for name, imp in zip(fi.feature_names, fi.importances)
            ]
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)

        # Build per-class metrics
        per_class_metrics = None
        if evaluation_result.metrics.per_class_metrics:
            per_class_metrics = [
                {
                    'class': pcm.class_name,
                    'precision': pcm.precision,
                    'recall': pcm.recall,
                    'f1': pcm.f1,
                    'support': pcm.support
                }
                for pcm in evaluation_result.metrics.per_class_metrics
            ]

        # Get class distribution for imbalance info
        class_distribution = None
        if hasattr(profile, 'class_distribution') and profile.class_distribution:
            class_distribution = profile.class_distribution

        return {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0'
            },
            'data_profile': {
                'n_rows': profile.n_rows,
                'n_cols': profile.n_cols,
                'numerical_columns': profile.numerical_columns,
                'categorical_columns': profile.categorical_columns,
                'target_column': profile.target_column,
                'target_unique_values': profile.target_unique_values,
                'is_imbalanced': profile.is_imbalanced,
                'class_distribution': class_distribution
            },
            'task_info': {
                'task_type': task_info.task_type.value,
                'n_classes': task_info.n_classes,
                'is_binary': task_info.is_binary,
                'is_multiclass': task_info.is_multiclass,
                'is_regression': task_info.is_regression
            },
            'training': {
                'best_model': training_report.best_model_name,
                'best_score': training_report.best_score,
                'scoring_metric': training_report.scoring_metric,
                'scoring_metric_description': self._get_metric_description(training_report.scoring_metric, task_info),
                'total_time': training_report.total_training_time,
                'results': training_results,
                'note': 'These scores are from cross-validation during model selection (not final test performance)'
            },
            'evaluation': {
                'metrics': metrics_dict,
                'confusion_matrix': evaluation_result.metrics.confusion_matrix.tolist() if evaluation_result.metrics.confusion_matrix is not None else None,
                'per_class_metrics': per_class_metrics,
                'note': 'These metrics are from a held-out test set (20% of data)'
            },
            'feature_importance': feature_importance
        }

    def export_json_report(
        self,
        report_data: Dict[str, Any],
        run_name: str
    ) -> Path:
        """Export report as JSON."""
        report_path = self.reports_dir / f"{run_name}_report.json"

        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        return report_path

    def export_html_report(
        self,
        report_data: Dict[str, Any],
        run_name: str
    ) -> Path:
        """Export report as HTML."""
        report_path = self.reports_dir / f"{run_name}_report.html"

        html_content = self._generate_html_report(report_data)

        with open(report_path, 'w') as f:
            f.write(html_content)

        return report_path

    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML report content."""
        task_type = report_data['task_info']['task_type']
        best_model = report_data['training']['best_model']
        best_score = report_data['training']['best_score']
        scoring_metric = report_data['training']['scoring_metric']
        scoring_metric_desc = report_data['training'].get('scoring_metric_description', '')
        metrics = report_data['evaluation']['metrics']
        is_imbalanced = report_data['data_profile'].get('is_imbalanced', False)

        # Build imbalance warning
        imbalance_warning = ""
        if is_imbalanced and not report_data['task_info']['is_regression']:
            imbalance_warning = """
            <div class="warning-box">
                <strong>Class Imbalance Detected</strong>
                <p>This dataset has imbalanced class distribution. The model may be biased toward the majority class.
                Consider using class balancing techniques or focusing on per-class metrics (especially recall for minority classes).</p>
            </div>
            """

        # Build test metrics table
        metrics_rows = ""
        for metric, value in metrics.items():
            metric_display = metric.upper().replace('_', ' ')
            metrics_rows += f"<tr><td>{metric_display}</td><td>{value:.4f}</td></tr>"

        # Build training results table (CV scores)
        training_rows = ""
        for result in report_data['training']['results']:
            best_marker = " <span class='best-badge'>BEST</span>" if result['is_best'] else ""
            training_rows += f"""
            <tr>
                <td>{result['model_name']}{best_marker}</td>
                <td>{result['mean_score']:.4f}</td>
                <td>+/- {result['std_score']:.4f}</td>
                <td>{result['training_time']:.1f}s</td>
            </tr>
            """

        # Build per-class metrics table
        per_class_rows = ""
        per_class_metrics = report_data['evaluation'].get('per_class_metrics')
        if per_class_metrics:
            for pcm in per_class_metrics:
                per_class_rows += f"""
                <tr>
                    <td>{pcm['class']}</td>
                    <td>{pcm['precision']:.4f}</td>
                    <td>{pcm['recall']:.4f}</td>
                    <td>{pcm['f1']:.4f}</td>
                    <td>{pcm['support']:,}</td>
                </tr>
                """

        # Build feature importance table
        feature_rows = ""
        if report_data['feature_importance']:
            for fi in report_data['feature_importance'][:10]:
                feature_rows += f"""
                <tr>
                    <td>{fi['feature']}</td>
                    <td>{fi['importance']:.4f}</td>
                </tr>
                """

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AutoML Training Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #666;
            margin-top: 30px;
        }}
        h3 {{
            color: #888;
            margin-top: 20px;
            font-size: 16px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .summary-box {{
            background: #e8f5e9;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .warning-box {{
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 15px 20px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .info-box {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 12px 16px;
            border-radius: 4px;
            margin: 10px 0;
            font-size: 14px;
        }}
        .metric {{
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }}
        .metric-name {{
            color: #666;
            font-size: 14px;
        }}
        .timestamp {{
            color: #999;
            font-size: 12px;
        }}
        .best-badge {{
            background: #4CAF50;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-left: 8px;
        }}
        .section-note {{
            color: #666;
            font-size: 13px;
            font-style: italic;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AutoML Training Report</h1>
        <p class="timestamp">Generated: {report_data['metadata']['timestamp']}</p>

        {imbalance_warning}

        <div class="summary-box">
            <h2>Summary</h2>
            <p><strong>Task Type:</strong> {task_type}</p>
            <p><strong>Best Model:</strong> {best_model}</p>
            <p><strong>Best CV Score:</strong> <span class="metric">{best_score:.4f}</span> <span class="metric-name">({scoring_metric})</span></p>
            <p><strong>Dataset Size:</strong> {report_data['data_profile']['n_rows']:,} rows x {report_data['data_profile']['n_cols']} columns</p>
        </div>

        <div class="info-box">
            <strong>Scoring Metric:</strong> {scoring_metric_desc}
        </div>

        <h2>Model Selection (Cross-Validation)</h2>
        <p class="section-note">Models were compared using {scoring_metric} scores from cross-validation on the training data.</p>
        <table>
            <tr>
                <th>Model</th>
                <th>CV Score</th>
                <th>Std Dev</th>
                <th>Training Time</th>
            </tr>
            {training_rows}
        </table>

        <h2>Test Set Performance</h2>
        <p class="section-note">Final evaluation metrics on a held-out test set (20% of data, not used during model selection).</p>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            {metrics_rows}
        </table>

        {"<h3>Per-Class Breakdown</h3><table><tr><th>Class</th><th>Precision</th><th>Recall</th><th>F1</th><th>Support</th></tr>" + per_class_rows + "</table>" if per_class_rows else ""}

        {"<h2>Top 10 Feature Importance</h2><p class='section-note'>Features most influential for model predictions. Importance values depend on the model type.</p><table><tr><th>Feature</th><th>Importance</th></tr>" + feature_rows + "</table>" if feature_rows else ""}

    </div>
</body>
</html>
        """

        return html

    def export_confusion_matrix(
        self,
        cm: np.ndarray,
        run_name: str
    ) -> Path:
        """Export confusion matrix as image."""
        cm_path = self.artifacts_dir / f"{run_name}_confusion_matrix.png"

        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(cm_path, dpi=150)
        plt.close()

        return cm_path

    def export_feature_importance(
        self,
        feature_names: List[str],
        importances: List[float],
        run_name: str,
        top_k: int = 15
    ) -> Path:
        """Export feature importance as image."""
        fi_path = self.artifacts_dir / f"{run_name}_feature_importance.png"

        # Sort and limit to top_k
        indices = np.argsort(importances)[::-1][:top_k]
        top_names = [feature_names[i] for i in indices]
        top_importances = [importances[i] for i in indices]

        plt.figure(figsize=(10, 6))
        plt.barh(range(len(top_names)), top_importances[::-1])
        plt.yticks(range(len(top_names)), top_names[::-1])
        plt.xlabel('Importance')
        plt.title('Feature Importance')
        plt.tight_layout()
        plt.savefig(fi_path, dpi=150)
        plt.close()

        return fi_path

    def load_model(self, model_path: str) -> Dict[str, Any]:
        """
        Load a saved model bundle.

        Args:
            model_path: Path to the model file

        Returns:
            Dictionary with 'model' and 'preprocessor'
        """
        return joblib.load(model_path)
