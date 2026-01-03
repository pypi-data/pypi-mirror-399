# TabuLaML

**Fast, explainable, no-code AutoML for tabular data.**

TabuLaML transforms raw CSV data into trained, deployable machine learning models with zero configuration. Just point it at your data and go.

## Installation

```bash
pip install tabulaml
```

With XGBoost and LightGBM support:
```bash
pip install tabulaml[all]
```

## Quick Start

```bash
tabulaml train data.csv --target target_column
```

Or use in Python:
```python
from automl import AutoMLPipeline

pipeline = AutoMLPipeline()
results = pipeline.run("data.csv", target_column="target")
```

## What It Does

- **Automatic Data Profiling** - Detects column types, missing values, cardinality, and class imbalance
- **Task Inference** - Automatically determines if your problem is binary classification, multiclass classification, or regression
- **Smart Preprocessing** - Handles missing values, scales numerical features, encodes categorical variables
- **Class Balancing** - Addresses imbalanced datasets using SMOTE, ADASYN, and other resampling techniques
- **Multi-Model Training** - Trains and compares Logistic Regression, Random Forest, Gradient Boosting, XGBoost, and LightGBM
- **Cross-Validation** - Selects the best model using rigorous cross-validation scoring
- **Export Ready** - Outputs trained models (.pkl), detailed reports (HTML/JSON), confusion matrices, and feature importance charts

## Output

After training, you'll find in the `outputs/` folder:

```
outputs/
  models/      - Trained model (.pkl)
  reports/     - HTML and JSON reports
  artifacts/   - Confusion matrix, feature importance charts
```

## Use Cases

| Context | What It Optimizes |
|---------|-------------------|
| Fraud Detection | Minimize missed fraud (high recall) |
| Churn Prediction | Catch at-risk customers before they leave |
| Medical Diagnosis | Reduce false negatives for critical conditions |
| Spam Detection | Minimize false positives to protect legitimate emails |
| Loan Approval | Balance risk assessment with approval rates |
| Marketing Campaigns | Target likely responders efficiently |
| Quality Control | Catch defective products before shipping |

## Key Features

- **Zero Configuration** - Point it at a CSV and go
- **Progress Bar** - Clean, user-friendly progress display
- **Explainable Results** - Understand why the model makes predictions
- **Reproducible** - Set random seeds for consistent results
- **Production Ready** - Export models ready for deployment

## Requirements

- Python 3.9+
- Works on Windows, macOS, and Linux

## License

MIT License - Copyright (c) 2025 Sekpey Herbert
