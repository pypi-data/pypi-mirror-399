"""
TabuLaML - CLI Interface

Usage:
    tabulaml train data.csv --target label
    tabulaml predict model.pkl new_data.csv
"""

import os
import sys
import json
import warnings

# Suppress joblib/loky resource tracker warnings on Windows
# This must be done BEFORE importing joblib or sklearn
if sys.platform == "win32":
    os.environ["LOKY_MAX_CPU_COUNT"] = str(os.cpu_count() or 4)
    os.environ["JOBLIB_START_METHOD"] = "spawn"
    # Use threading backend to avoid multiprocessing resource tracker issues
    try:
        from joblib import parallel_config
        parallel_config(backend="threading")
    except ImportError:
        pass

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="joblib")
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.utils.parallel")
warnings.filterwarnings("ignore", message=".*resource_tracker.*")
warnings.filterwarnings("ignore", message=".*loky.*")
warnings.filterwarnings("ignore", message=".*sklearn.utils.parallel.delayed.*")

import click
import pandas as pd
from pathlib import Path

from .pipeline import AutoMLPipeline


def load_csv_smart(file_path: str) -> pd.DataFrame:
    """
    Load CSV with automatic delimiter detection.

    Handles common delimiters: comma, semicolon, tab.
    """
    import csv

    # Detect delimiter
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        sample = f.read(4096)

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = ','

    df = pd.read_csv(file_path, delimiter=delimiter)

    # Fallback if still 1 column
    if len(df.columns) == 1:
        col_name = df.columns[0]
        if ';' in col_name:
            df = pd.read_csv(file_path, delimiter=';')
        elif '\t' in col_name:
            df = pd.read_csv(file_path, delimiter='\t')

    return df


def find_csv_files(directory: str = ".", recursive: bool = True) -> list:
    """Find all CSV files in a directory."""
    csv_files = []
    path = Path(directory)

    if recursive:
        csv_files = list(path.rglob("*.csv"))
    else:
        csv_files = list(path.glob("*.csv"))

    # Filter out files in venv, __pycache__, etc.
    exclude_dirs = {'venv', '__pycache__', '.git', 'node_modules', 'outputs'}
    csv_files = [
        f for f in csv_files
        if not any(excluded in f.parts for excluded in exclude_dirs)
    ]

    return sorted(csv_files, key=lambda x: x.stat().st_mtime, reverse=True)


def select_file_interactive() -> str:
    """Interactive file selection menu."""
    click.echo("\n" + "=" * 60)
    click.echo("  TabuLaML - FILE SELECTION")
    click.echo("=" * 60)

    # Find CSV files in current directory
    csv_files = find_csv_files(".")

    if not csv_files:
        click.echo("\nNo CSV files found in current directory.")
        click.echo("Options:")
        click.echo("  1. Enter a file path manually")
        click.echo("  2. Exit")

        choice = click.prompt("\nSelect option", type=int, default=1)

        if choice == 1:
            file_path = click.prompt("Enter the full path to your CSV file")
            if Path(file_path).exists():
                return file_path
            else:
                click.echo(f"Error: File '{file_path}' not found.")
                raise click.Abort()
        else:
            raise click.Abort()

    click.echo(f"\nFound {len(csv_files)} CSV file(s):\n")

    for i, csv_file in enumerate(csv_files[:10], 1):
        # Get file size
        size = csv_file.stat().st_size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"

        click.echo(f"  [{i}] {csv_file} ({size_str})")

    if len(csv_files) > 10:
        click.echo(f"\n  ... and {len(csv_files) - 10} more files")

    click.echo(f"\n  [0] Enter a different file path")
    click.echo(f"  [q] Quit")

    choice = click.prompt("\nSelect a file", default="1")

    if choice.lower() == 'q':
        raise click.Abort()

    if choice == '0':
        file_path = click.prompt("Enter the full path to your CSV file")
        if Path(file_path).exists():
            return file_path
        else:
            click.echo(f"Error: File '{file_path}' not found.")
            raise click.Abort()

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(csv_files):
            return str(csv_files[idx])
        else:
            click.echo("Invalid selection.")
            raise click.Abort()
    except ValueError:
        click.echo("Invalid input.")
        raise click.Abort()


def select_context() -> str:
    """Interactive business context selection."""
    click.echo("\n" + "-" * 60)
    click.echo("  SELECT BUSINESS CONTEXT")
    click.echo("-" * 60)

    contexts = [
        ("fraud_detection", "Fraud Detection", "Catch all fraud (optimizes recall)"),
        ("churn_prediction", "Churn Prediction", "Identify at-risk customers (optimizes recall)"),
        ("medical_diagnosis", "Medical Diagnosis", "Don't miss any disease (optimizes recall)"),
        ("spam_detection", "Spam Detection", "Don't block good emails (optimizes precision)"),
        ("loan_approval", "Loan Approval", "Balance risk vs opportunity (optimizes F1)"),
        ("marketing_campaign", "Marketing Campaign", "Target likely responders (optimizes precision)"),
        ("quality_control", "Quality Control", "Catch all defects (optimizes recall)"),
    ]

    click.echo("\nWhat type of problem are you solving?\n")

    for i, (ctx_id, name, desc) in enumerate(contexts, 1):
        click.echo(f"  [{i}] {name}")
        click.echo(f"      {desc}")

    click.echo(f"\n  [0] No specific context (use default F1 optimization)")

    choice = click.prompt("\nSelect context", default="0")

    if choice == '0':
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(contexts):
            selected = contexts[idx]
            click.echo(f"\nSelected: {selected[1]}")
            return selected[0]
        else:
            click.echo("Invalid selection, using default.")
            return None
    except ValueError:
        click.echo("Invalid input, using default.")
        return None


def select_target_column(df: pd.DataFrame) -> str:
    """Interactive target column selection."""
    click.echo("\n" + "-" * 60)
    click.echo("  SELECT TARGET COLUMN")
    click.echo("-" * 60)

    columns = list(df.columns)

    click.echo(f"\nAvailable columns ({len(columns)}):\n")

    for i, col in enumerate(columns, 1):
        dtype = df[col].dtype
        unique = df[col].nunique()
        nulls = df[col].isnull().sum()

        # Suggest likely targets
        suggestion = ""
        if col.lower() in ['target', 'label', 'class', 'y', 'output', 'result']:
            suggestion = " <- likely target"
        elif i == len(columns):
            suggestion = " <- last column"

        click.echo(f"  [{i}] {col} (dtype: {dtype}, unique: {unique}, nulls: {nulls}){suggestion}")

    click.echo(f"\n  [0] Auto-detect target column")

    choice = click.prompt("\nSelect target column", default="0")

    if choice == '0':
        return None  # Auto-detect

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(columns):
            return columns[idx]
        else:
            click.echo("Invalid selection, using auto-detect.")
            return None
    except ValueError:
        click.echo("Invalid input, using auto-detect.")
        return None


@click.group()
@click.version_option(version='0.1.0', prog_name='tabulaml')
def cli():
    """
    TabuLaML - Fast, Explainable AutoML for Tabular Data

    A command-line tool for automated machine learning that:

    \b
    - Profiles your data automatically
    - Infers the ML task type (classification/regression)
    - Preprocesses data (imputation, scaling, encoding)
    - Trains multiple models (Logistic Regression, Random Forest, XGBoost, LightGBM)
    - Selects the best performer using cross-validation
    - Exports model (.pkl) and reports (HTML/JSON)

    \b
    Quick Start:
        tabulaml train data.csv
        tabulaml train  # Interactive mode
    """
    pass


@cli.command()
@click.argument('data_path', type=click.Path(exists=True), required=False)
@click.option('--target', '-t', default=None, help='Target column name (auto-detected if not provided)')
@click.option('--output', '-o', default='outputs', help='Output directory for models and reports')
@click.option('--name', '-n', default=None, help='Name for this training run')
@click.option('--cv-folds', default=3, help='Number of cross-validation folds')
@click.option('--no-xgboost', is_flag=True, help='Disable XGBoost models')
@click.option('--no-lightgbm', is_flag=True, help='Disable LightGBM models')
@click.option('--no-balance', is_flag=True, help='Disable class balancing for imbalanced datasets')
@click.option('--balance-strategy', default='auto',
              type=click.Choice(['auto', 'smote', 'adasyn', 'random_over', 'random_under', 'smote_tomek', 'smote_enn', 'none']),
              help='Strategy for class balancing (default: auto)')
@click.option('--class-weight', default=None,
              type=click.Choice(['balanced', 'balanced_subsample']),
              help='Class weighting for imbalanced data (alternative to SMOTE)')
@click.option('--context', '-c', default=None,
              type=click.Choice(['fraud_detection', 'churn_prediction', 'medical_diagnosis',
                                'spam_detection', 'loan_approval', 'marketing_campaign',
                                'quality_control']),
              help='Business context for optimization (optimizes metric & threshold)')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed technical output')
@click.option('--quiet', '-q', is_flag=True, help='Completely silent (no output at all)')
@click.option('--seed', default=42, help='Random seed for reproducibility')
@click.option('--keep-leaked', is_flag=True, help='Keep leaked features instead of dropping them')
@click.option('--aggressive-drop', is_flag=True, help='Also drop MEDIUM risk features (may cause false positives)')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode for file and target selection')
def train(data_path, target, output, name, cv_folds, no_xgboost, no_lightgbm, no_balance, balance_strategy, class_weight, context, verbose, quiet, seed, keep_leaked, aggressive_drop, interactive):
    """
    Run the TabuLaML pipeline on a CSV dataset.

    \b
    DATA_PATH: Path to the input CSV file (optional - will prompt if not provided)

    \b
    Examples:
        tabulaml train                          # Interactive file selection
        tabulaml train data.csv                 # Direct file path
        tabulaml train data.csv --target label  # Specify target column
        tabulaml train data.csv -o results      # Custom output directory
        tabulaml train -i                       # Force interactive mode
    """
    # If no data path provided, enter interactive mode
    if data_path is None:
        interactive = True
        data_path = select_file_interactive()

    click.echo(f"\nSelected file: {data_path}")

    # Preview data and select target/context interactively
    if interactive:
        # Smart CSV loading with delimiter detection
        df = load_csv_smart(data_path)
        click.echo(f"Dataset preview: {len(df):,} rows x {len(df.columns)} columns")

        # Show first few rows
        click.echo("\nFirst 5 rows:")
        click.echo(df.head().to_string())

        if target is None:
            target = select_target_column(df)

    # Always prompt for context if not provided (key feature!)
    if context is None and not quiet:
        context = select_context()

    # Generate run name if not provided
    if name is None:
        name = Path(data_path).stem

    click.echo(f"\nStarting TabuLaML pipeline...")
    click.echo(f"  File: {data_path}")
    click.echo(f"  Target: {target if target else 'auto-detect'}")
    click.echo(f"  Output: {output}")
    click.echo(f"  Run name: {name}")
    if context:
        click.echo(f"  Context: {context.replace('_', ' ').title()}")

    pipeline = AutoMLPipeline(
        output_dir=output,
        random_state=seed,
        cv_folds=cv_folds,
        use_xgboost=not no_xgboost,
        use_lightgbm=not no_lightgbm,
        balance_classes=not no_balance,
        balance_strategy=balance_strategy,
        class_weight=class_weight,
        verbose=verbose,
        quiet=quiet,
        drop_leaked_features=not keep_leaked,
        aggressive_leakage_drop=aggressive_drop,
        context=context
    )

    results = pipeline.run(
        data_path=data_path,
        target_column=target,
        run_name=name
    )

    click.echo(f"\nBest model: {results['best_model_name']}")
    click.echo(f"Best score: {results['best_score']:.4f}")

    # Show context-specific results
    if results.get('threshold_result') and results['threshold_result'].optimal_threshold != 0.5:
        tr = results['threshold_result']
        click.echo(f"\nContext-Aware Optimization:")
        click.echo(f"  Optimized threshold: {tr.optimal_threshold:.2f} (default: 0.50)")
        click.echo(f"  {tr.metric_name.capitalize()} improvement: +{tr.improvement:.4f}")

    # Show leakage warnings
    leakage_report = results.get('leakage_report')
    if leakage_report and leakage_report.high_risk_features:
        click.echo(f"\nLeakage Warning:")
        for feature in leakage_report.high_risk_features[:3]:
            click.echo(f"  - {feature}")
        if len(leakage_report.high_risk_features) > 3:
            click.echo(f"  ... and {len(leakage_report.high_risk_features) - 3} more")

    # Show readiness score
    readiness = results.get('readiness_score')
    if readiness:
        level_emoji = {
            'ready': '[OK]',
            'caution': '[!]',
            'review': '[?]',
            'not_ready': '[X]'
        }
        emoji = level_emoji.get(readiness.readiness_level.value, '')
        click.echo(f"\nProduction Readiness: {readiness.overall_score:.0f}/100 {emoji} {readiness.readiness_level.value.upper()}")

    click.echo(f"\nModel saved to: {results['export_paths'].model_path}")
    click.echo(f"Report saved to: {results['export_paths'].report_html_path}")


@cli.command()
@click.argument('model_path', type=click.Path(exists=True), required=False)
@click.argument('data_path', type=click.Path(exists=True), required=False)
@click.option('--output', '-o', default=None, help='Output CSV path for predictions')
@click.option('--proba', is_flag=True, help='Output probabilities instead of class labels')
def predict(model_path, data_path, output, proba):
    """
    Make predictions using a trained model.

    \b
    MODEL_PATH: Path to the trained model (.pkl file)
    DATA_PATH: Path to the input CSV file for predictions

    \b
    Examples:
        tabulaml predict                              # Interactive selection
        tabulaml predict outputs/models/model.pkl new_data.csv
        tabulaml predict model.pkl data.csv -o predictions.csv
        tabulaml predict model.pkl data.csv --proba  # Get probabilities
    """
    # Interactive model selection if not provided
    if model_path is None:
        models_dir = Path("outputs/models")
        if models_dir.exists():
            model_files = list(models_dir.glob("*.pkl"))
            if model_files:
                click.echo("\nAvailable models:")
                for i, mf in enumerate(model_files, 1):
                    click.echo(f"  [{i}] {mf}")

                choice = click.prompt("Select a model", type=int, default=1)
                if 1 <= choice <= len(model_files):
                    model_path = str(model_files[choice - 1])
                else:
                    click.echo("Invalid selection.")
                    raise click.Abort()
            else:
                model_path = click.prompt("Enter path to model file")
        else:
            model_path = click.prompt("Enter path to model file")

    # Interactive data selection if not provided
    if data_path is None:
        data_path = select_file_interactive()

    click.echo(f"Loading model from {model_path}")

    pipeline = AutoMLPipeline(verbose=False)

    # Load data
    df = pd.read_csv(data_path)
    click.echo(f"Loaded {len(df)} rows for prediction")

    # Make predictions
    if proba:
        predictions = pipeline.predict_proba(df, model_path=model_path)
    else:
        predictions = pipeline.predict(df, model_path=model_path)

    # Output results
    if output:
        if proba:
            # For probabilities, create columns for each class
            pred_df = pd.DataFrame(
                predictions,
                columns=[f'prob_class_{i}' for i in range(predictions.shape[1])]
            )
        else:
            pred_df = pd.DataFrame({'prediction': predictions})

        pred_df.to_csv(output, index=False)
        click.echo(f"Predictions saved to {output}")
    else:
        click.echo("\nPredictions:")
        for i, pred in enumerate(predictions[:10]):
            click.echo(f"  {i}: {pred}")
        if len(predictions) > 10:
            click.echo(f"  ... and {len(predictions) - 10} more")


@cli.command()
@click.argument('data_path', type=click.Path(exists=True), required=False)
@click.option('--target', '-t', default=None, help='Target column name')
def profile(data_path, target):
    """
    Profile a dataset without training.

    \b
    DATA_PATH: Path to the CSV file to profile

    \b
    Examples:
        tabulaml profile                  # Interactive file selection
        tabulaml profile data.csv
        tabulaml profile data.csv --target label
    """
    from .profiler import DataProfiler
    from .task_inference import TaskInferrer

    # Interactive file selection if not provided
    if data_path is None:
        data_path = select_file_interactive()

    click.echo(f"Profiling {data_path}")

    df = pd.read_csv(data_path)

    profiler = DataProfiler()
    prof = profiler.profile(df, target)
    click.echo(profiler.get_summary(prof))

    inferrer = TaskInferrer()
    task_info = inferrer.infer(df, prof)
    click.echo(inferrer.get_summary(task_info))


@cli.command()
@click.argument('report_path', type=click.Path(exists=True), required=False)
def show(report_path):
    """
    Display a training report.

    \b
    REPORT_PATH: Path to the JSON report file

    \b
    Examples:
        tabulaml show                             # Interactive selection
        tabulaml show outputs/reports/report.json
    """
    # Interactive report selection if not provided
    if report_path is None:
        reports_dir = Path("outputs/reports")
        if reports_dir.exists():
            report_files = list(reports_dir.glob("*.json"))
            if report_files:
                click.echo("\nAvailable reports:")
                for i, rf in enumerate(report_files, 1):
                    click.echo(f"  [{i}] {rf}")

                choice = click.prompt("Select a report", type=int, default=1)
                if 1 <= choice <= len(report_files):
                    report_path = str(report_files[choice - 1])
                else:
                    click.echo("Invalid selection.")
                    raise click.Abort()
            else:
                report_path = click.prompt("Enter path to report file")
        else:
            report_path = click.prompt("Enter path to report file")

    with open(report_path) as f:
        report = json.load(f)

    click.echo("=" * 60)
    click.echo("TRAINING REPORT")
    click.echo("=" * 60)

    click.echo(f"\nTimestamp: {report['metadata']['timestamp']}")
    click.echo(f"Task Type: {report['task_info']['task_type']}")
    click.echo(f"Dataset: {report['data_profile']['n_rows']:,} rows x {report['data_profile']['n_cols']} columns")

    click.echo(f"\nBest Model: {report['training']['best_model']}")
    click.echo(f"Best Score: {report['training']['best_score']:.4f}")

    click.echo("\nMetrics:")
    for metric, value in report['evaluation']['metrics'].items():
        click.echo(f"  {metric}: {value:.4f}")

    click.echo("\nModel Rankings:")
    for result in report['training']['results']:
        best = " *BEST*" if result['is_best'] else ""
        click.echo(f"  {result['model_name']}: {result['mean_score']:.4f}{best}")


@cli.command()
@click.argument('report_path', type=click.Path(exists=True), required=False)
@click.option('--context', '-c',
              type=click.Choice(['fraud_detection', 'churn_prediction', 'medical_diagnosis',
                                'spam_detection', 'loan_approval', 'marketing_campaign',
                                'quality_control', 'all']),
              default='all',
              help='Business context for analysis')
@click.option('--fp-cost', type=float, default=None, help='Cost per False Positive (for cost analysis)')
@click.option('--fn-cost', type=float, default=None, help='Cost per False Negative (for cost analysis)')
def analyze(report_path, context, fp_cost, fn_cost):
    """
    Analyze model performance in different business contexts.

    Provides context-aware interpretation of model results, showing how
    the same confusion matrix has different implications for different use cases.

    \b
    REPORT_PATH: Path to the JSON report file

    \b
    Available contexts:
        fraud_detection   - Fraud/anomaly detection (FN is critical)
        churn_prediction  - Customer churn prediction (FN is costly)
        medical_diagnosis - Disease screening (FN is dangerous)
        spam_detection    - Email spam filtering (FP is critical)
        loan_approval     - Credit risk assessment (balanced)
        marketing_campaign - Campaign targeting (precision matters)
        quality_control   - Defect detection (FN is critical)
        all               - Show analysis for all contexts

    \b
    Examples:
        tabulaml analyze                                    # Interactive
        tabulaml analyze report.json                        # All contexts
        tabulaml analyze report.json -c fraud_detection    # Specific context
        tabulaml analyze report.json -c churn_prediction --fp-cost 10 --fn-cost 500
    """
    from .business_context import BusinessContextEvaluator, BusinessContext
    import numpy as np

    # Interactive report selection if not provided
    if report_path is None:
        reports_dir = Path("outputs/reports")
        if reports_dir.exists():
            report_files = list(reports_dir.glob("*.json"))
            if report_files:
                click.echo("\nAvailable reports:")
                for i, rf in enumerate(report_files, 1):
                    click.echo(f"  [{i}] {rf}")

                choice = click.prompt("Select a report", type=int, default=1)
                if 1 <= choice <= len(report_files):
                    report_path = str(report_files[choice - 1])
                else:
                    click.echo("Invalid selection.")
                    raise click.Abort()
            else:
                report_path = click.prompt("Enter path to report file")
        else:
            report_path = click.prompt("Enter path to report file")

    with open(report_path) as f:
        report = json.load(f)

    # Check if this is a classification task
    task_type = report.get('task_info', {}).get('task_type', '')
    if 'regression' in task_type.lower():
        click.echo("Business context analysis is only available for classification tasks.")
        raise click.Abort()

    # Get confusion matrix from report
    confusion_matrix = report.get('evaluation', {}).get('confusion_matrix')
    if confusion_matrix is None:
        click.echo("No confusion matrix found in report.")
        raise click.Abort()

    cm = np.array(confusion_matrix)

    click.echo("\n" + "=" * 60)
    click.echo("BUSINESS CONTEXT ANALYSIS")
    click.echo("=" * 60)
    click.echo(f"\nReport: {report_path}")
    click.echo(f"Model: {report['training']['best_model']}")
    click.echo(f"Task: {task_type}")

    # Determine which contexts to analyze
    if context == 'all':
        contexts_to_analyze = [
            BusinessContext.FRAUD_DETECTION,
            BusinessContext.CHURN_PREDICTION,
            BusinessContext.MEDICAL_DIAGNOSIS,
            BusinessContext.SPAM_DETECTION,
            BusinessContext.LOAN_APPROVAL,
            BusinessContext.MARKETING_CAMPAIGN,
            BusinessContext.QUALITY_CONTROL,
        ]
    else:
        contexts_to_analyze = [BusinessContext(context)]

    # Analyze each context
    for biz_context in contexts_to_analyze:
        evaluator = BusinessContextEvaluator(
            context=biz_context,
            fp_cost=fp_cost,
            fn_cost=fn_cost
        )
        insight = evaluator.evaluate(cm)
        click.echo(evaluator.get_summary(insight))


@cli.command('list-contexts')
def list_contexts():
    """
    List all available business contexts with descriptions.

    \b
    Examples:
        tabulaml list-contexts
    """
    from .business_context import BusinessContextEvaluator

    contexts = BusinessContextEvaluator.list_available_contexts()

    click.echo("\n" + "=" * 60)
    click.echo("AVAILABLE BUSINESS CONTEXTS")
    click.echo("=" * 60)

    for ctx in contexts:
        click.echo(f"\n{ctx['name'].upper()}")
        click.echo("-" * 40)
        click.echo(f"  ID: {ctx['id']}")
        click.echo(f"  Description: {ctx['description']}")
        click.echo(f"  Priority Metric: {ctx['priority_metric']}")
        click.echo(f"  FP Cost Level: {ctx['fp_cost_level']}")
        click.echo(f"  FN Cost Level: {ctx['fn_cost_level']}")

    click.echo("\n" + "=" * 60)
    click.echo("Usage: tabulaml analyze report.json -c <context_id>")
    click.echo("=" * 60)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
