"""
Business Context Evaluator Module

Provides business-context-aware interpretation of model performance.
Different use cases have different costs for False Positives vs False Negatives.

Supported contexts:
- Fraud Detection: FN is costly (missed fraud), FP is annoying (blocked transactions)
- Churn Prediction: FN is costly (lost customers), FP wastes retention efforts
- Medical Diagnosis: FN can be dangerous (missed disease), FP causes anxiety/costs
- Spam Detection: FP is very bad (missed emails), FN is annoying
- Loan Approval: FN = approving risky loans (defaults), FP = rejecting good customers
- Marketing Campaign: FN = missed opportunities, FP = wasted spend
- Quality Control: FN = defective products shipped, FP = good products rejected
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Literal
from enum import Enum
import numpy as np


class BusinessContext(Enum):
    """Supported business contexts for model evaluation."""
    FRAUD_DETECTION = "fraud_detection"
    CHURN_PREDICTION = "churn_prediction"
    MEDICAL_DIAGNOSIS = "medical_diagnosis"
    SPAM_DETECTION = "spam_detection"
    LOAN_APPROVAL = "loan_approval"
    MARKETING_CAMPAIGN = "marketing_campaign"
    QUALITY_CONTROL = "quality_control"
    CUSTOM = "custom"


@dataclass
class ContextConfig:
    """Configuration for a business context."""
    name: str
    description: str
    positive_class_meaning: str  # What does class 1 represent?
    negative_class_meaning: str  # What does class 0 represent?
    fp_description: str  # What does a False Positive mean?
    fn_description: str  # What does a False Negative mean?
    fp_cost_level: Literal["low", "medium", "high", "critical"]
    fn_cost_level: Literal["low", "medium", "high", "critical"]
    priority_metric: str  # Which metric matters most?
    threshold_recommendation: str  # How to adjust threshold


# Predefined business contexts
CONTEXT_CONFIGS: Dict[BusinessContext, ContextConfig] = {
    BusinessContext.FRAUD_DETECTION: ContextConfig(
        name="Fraud Detection",
        description="Identifying fraudulent transactions or activities",
        positive_class_meaning="Fraud",
        negative_class_meaning="Legitimate",
        fp_description="Blocking legitimate transactions (customer friction)",
        fn_description="Missing fraudulent transactions (financial loss)",
        fp_cost_level="medium",
        fn_cost_level="critical",
        priority_metric="recall",
        threshold_recommendation="Lower threshold to catch more fraud, accept more false alarms"
    ),
    BusinessContext.CHURN_PREDICTION: ContextConfig(
        name="Churn Prediction",
        description="Predicting which customers will leave/cancel",
        positive_class_meaning="Will Churn",
        negative_class_meaning="Will Stay",
        fp_description="Targeting loyal customers with retention offers (wasted resources)",
        fn_description="Missing customers who will churn (lost revenue)",
        fp_cost_level="low",
        fn_cost_level="high",
        priority_metric="recall",
        threshold_recommendation="Lower threshold to catch more churners, retention offers are cheap"
    ),
    BusinessContext.MEDICAL_DIAGNOSIS: ContextConfig(
        name="Medical Diagnosis",
        description="Screening for diseases or medical conditions",
        positive_class_meaning="Disease Present",
        negative_class_meaning="Healthy",
        fp_description="False alarm - unnecessary tests/anxiety for healthy patients",
        fn_description="Missed diagnosis - untreated disease (potentially dangerous)",
        fp_cost_level="medium",
        fn_cost_level="critical",
        priority_metric="recall",
        threshold_recommendation="Lower threshold significantly - missing disease is unacceptable"
    ),
    BusinessContext.SPAM_DETECTION: ContextConfig(
        name="Spam Detection",
        description="Filtering spam emails or messages",
        positive_class_meaning="Spam",
        negative_class_meaning="Legitimate Email",
        fp_description="Blocking important emails (very bad user experience)",
        fn_description="Letting spam through (annoying but recoverable)",
        fp_cost_level="critical",
        fn_cost_level="low",
        priority_metric="precision",
        threshold_recommendation="Higher threshold to avoid blocking legitimate emails"
    ),
    BusinessContext.LOAN_APPROVAL: ContextConfig(
        name="Loan Approval",
        description="Deciding whether to approve loan applications",
        positive_class_meaning="Will Default",
        negative_class_meaning="Will Repay",
        fp_description="Rejecting good customers (lost business opportunity)",
        fn_description="Approving risky customers (potential default/loss)",
        fp_cost_level="medium",
        fn_cost_level="high",
        priority_metric="f1",
        threshold_recommendation="Balance based on default cost vs customer acquisition value"
    ),
    BusinessContext.MARKETING_CAMPAIGN: ContextConfig(
        name="Marketing Campaign",
        description="Targeting customers for marketing campaigns",
        positive_class_meaning="Will Respond",
        negative_class_meaning="Won't Respond",
        fp_description="Sending offers to uninterested customers (wasted marketing spend)",
        fn_description="Missing potential customers (lost sales opportunity)",
        fp_cost_level="low",
        fn_cost_level="medium",
        priority_metric="precision",
        threshold_recommendation="Depends on campaign cost - expensive campaigns need higher precision"
    ),
    BusinessContext.QUALITY_CONTROL: ContextConfig(
        name="Quality Control",
        description="Detecting defective products in manufacturing",
        positive_class_meaning="Defective",
        negative_class_meaning="Good Quality",
        fp_description="Rejecting good products (waste, reduced yield)",
        fn_description="Shipping defective products (customer complaints, recalls)",
        fp_cost_level="medium",
        fn_cost_level="critical",
        priority_metric="recall",
        threshold_recommendation="Lower threshold - catching defects is more important than yield"
    ),
}


@dataclass
class BusinessInsight:
    """Container for business-context-aware insights."""
    context: BusinessContext
    config: ContextConfig
    confusion_matrix: np.ndarray

    # Counts
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int

    # Rates
    precision: float
    recall: float
    specificity: float
    f1_score: float

    # Business interpretation
    fp_interpretation: str
    fn_interpretation: str
    overall_assessment: str
    risk_level: Literal["low", "medium", "high", "critical"]
    recommendations: List[str]

    # Cost analysis (if costs provided)
    estimated_cost: Optional[float] = None
    cost_breakdown: Optional[Dict[str, float]] = None


class BusinessContextEvaluator:
    """
    Evaluates model performance in the context of specific business use cases.

    Different business contexts have different tolerance for False Positives
    vs False Negatives. This evaluator provides context-aware interpretation
    and recommendations.
    """

    def __init__(
        self,
        context: BusinessContext = BusinessContext.FRAUD_DETECTION,
        fp_cost: Optional[float] = None,
        fn_cost: Optional[float] = None,
        custom_config: Optional[ContextConfig] = None
    ):
        """
        Initialize the business context evaluator.

        Args:
            context: The business context for evaluation
            fp_cost: Optional cost per False Positive (for cost-sensitive analysis)
            fn_cost: Optional cost per False Negative (for cost-sensitive analysis)
            custom_config: Optional custom configuration for CUSTOM context
        """
        self.context = context
        self.fp_cost = fp_cost
        self.fn_cost = fn_cost

        if context == BusinessContext.CUSTOM and custom_config:
            self.config = custom_config
        elif context in CONTEXT_CONFIGS:
            self.config = CONTEXT_CONFIGS[context]
        else:
            raise ValueError(f"Unknown context: {context}")

    def evaluate(
        self,
        confusion_matrix: np.ndarray,
        class_labels: Optional[List[str]] = None
    ) -> BusinessInsight:
        """
        Evaluate model performance in the business context.

        Args:
            confusion_matrix: 2x2 confusion matrix [[TN, FP], [FN, TP]]
            class_labels: Optional labels for classes

        Returns:
            BusinessInsight with context-aware interpretation
        """
        # Extract confusion matrix values
        # sklearn format: [[TN, FP], [FN, TP]]
        tn, fp, fn, tp = confusion_matrix.ravel()

        # Calculate metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Generate interpretations
        fp_interpretation = self._interpret_fp(fp, tn)
        fn_interpretation = self._interpret_fn(fn, tp)
        overall_assessment = self._assess_overall(tp, tn, fp, fn, precision, recall)
        risk_level = self._assess_risk(fp, fn, precision, recall)
        recommendations = self._generate_recommendations(tp, tn, fp, fn, precision, recall)

        # Calculate costs if provided
        estimated_cost = None
        cost_breakdown = None
        if self.fp_cost is not None and self.fn_cost is not None:
            fp_total_cost = fp * self.fp_cost
            fn_total_cost = fn * self.fn_cost
            estimated_cost = fp_total_cost + fn_total_cost
            cost_breakdown = {
                "false_positive_cost": fp_total_cost,
                "false_negative_cost": fn_total_cost,
                "total_cost": estimated_cost,
                "cost_per_prediction": estimated_cost / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
            }

        return BusinessInsight(
            context=self.context,
            config=self.config,
            confusion_matrix=confusion_matrix,
            true_positives=int(tp),
            true_negatives=int(tn),
            false_positives=int(fp),
            false_negatives=int(fn),
            precision=precision,
            recall=recall,
            specificity=specificity,
            f1_score=f1,
            fp_interpretation=fp_interpretation,
            fn_interpretation=fn_interpretation,
            overall_assessment=overall_assessment,
            risk_level=risk_level,
            recommendations=recommendations,
            estimated_cost=estimated_cost,
            cost_breakdown=cost_breakdown
        )

    def _interpret_fp(self, fp: int, tn: int) -> str:
        """Generate interpretation for False Positives."""
        total_negatives = fp + tn
        fp_rate = fp / total_negatives if total_negatives > 0 else 0

        if fp == 0:
            return f"Excellent: Zero {self.config.fp_description.lower()}"
        elif fp_rate < 0.05:
            return f"Good: Only {fp} cases of {self.config.fp_description.lower()} ({fp_rate:.1%} of negatives)"
        elif fp_rate < 0.15:
            return f"Acceptable: {fp} cases of {self.config.fp_description.lower()} ({fp_rate:.1%} of negatives)"
        else:
            return f"Warning: {fp} cases of {self.config.fp_description.lower()} ({fp_rate:.1%} of negatives) - may need attention"

    def _interpret_fn(self, fn: int, tp: int) -> str:
        """Generate interpretation for False Negatives."""
        total_positives = fn + tp
        fn_rate = fn / total_positives if total_positives > 0 else 0

        if fn == 0:
            return f"Excellent: Zero {self.config.fn_description.lower()}"
        elif fn_rate < 0.05:
            return f"Good: Only {fn} cases of {self.config.fn_description.lower()} ({fn_rate:.1%} miss rate)"
        elif fn_rate < 0.20:
            return f"Moderate: {fn} cases of {self.config.fn_description.lower()} ({fn_rate:.1%} miss rate)"
        elif fn_rate < 0.50:
            return f"Concerning: {fn} cases of {self.config.fn_description.lower()} ({fn_rate:.1%} miss rate)"
        else:
            return f"Critical: {fn} cases of {self.config.fn_description.lower()} ({fn_rate:.1%} miss rate) - needs improvement"

    def _assess_overall(
        self,
        tp: int, tn: int, fp: int, fn: int,
        precision: float, recall: float
    ) -> str:
        """Generate overall assessment based on business context."""
        total = tp + tn + fp + fn
        accuracy = (tp + tn) / total if total > 0 else 0

        # Context-specific assessment
        if self.config.fn_cost_level == "critical":
            # High FN cost contexts (fraud, medical, quality)
            if recall >= 0.95:
                return f"Excellent for {self.config.name}: Catching {recall:.1%} of {self.config.positive_class_meaning.lower()} cases"
            elif recall >= 0.80:
                return f"Good for {self.config.name}: Catching {recall:.1%} of {self.config.positive_class_meaning.lower()} cases, but consider lowering threshold"
            elif recall >= 0.50:
                return f"Risky for {self.config.name}: Missing {1-recall:.1%} of {self.config.positive_class_meaning.lower()} cases - threshold adjustment needed"
            else:
                return f"Dangerous for {self.config.name}: Missing {1-recall:.1%} of {self.config.positive_class_meaning.lower()} cases - model needs retraining or threshold adjustment"

        elif self.config.fp_cost_level == "critical":
            # High FP cost contexts (spam detection)
            if precision >= 0.99:
                return f"Excellent for {self.config.name}: {precision:.1%} precision means minimal false alarms"
            elif precision >= 0.95:
                return f"Good for {self.config.name}: {precision:.1%} precision is acceptable"
            elif precision >= 0.90:
                return f"Moderate for {self.config.name}: {1-precision:.1%} false alarm rate may frustrate users"
            else:
                return f"Problematic for {self.config.name}: {1-precision:.1%} false alarm rate is too high"

        else:
            # Balanced contexts (loan approval, marketing)
            if precision >= 0.80 and recall >= 0.80:
                return f"Well-balanced for {self.config.name}: Good precision ({precision:.1%}) and recall ({recall:.1%})"
            elif precision >= 0.70 and recall >= 0.70:
                return f"Acceptable for {self.config.name}: Precision {precision:.1%}, Recall {recall:.1%}"
            else:
                return f"Needs improvement for {self.config.name}: Consider adjusting threshold or retraining"

    def _assess_risk(
        self,
        fp: int, fn: int,
        precision: float, recall: float
    ) -> Literal["low", "medium", "high", "critical"]:
        """Assess overall risk level based on business context."""
        # Priority metric based on context
        if self.config.priority_metric == "recall":
            if recall >= 0.95:
                return "low"
            elif recall >= 0.80:
                return "medium"
            elif recall >= 0.50:
                return "high"
            else:
                return "critical"
        elif self.config.priority_metric == "precision":
            if precision >= 0.95:
                return "low"
            elif precision >= 0.85:
                return "medium"
            elif precision >= 0.70:
                return "high"
            else:
                return "critical"
        else:  # f1 or balanced
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            if f1 >= 0.85:
                return "low"
            elif f1 >= 0.70:
                return "medium"
            elif f1 >= 0.50:
                return "high"
            else:
                return "critical"

    def _generate_recommendations(
        self,
        tp: int, tn: int, fp: int, fn: int,
        precision: float, recall: float
    ) -> List[str]:
        """Generate actionable recommendations based on performance."""
        recommendations = []

        total_positives = tp + fn
        total_negatives = tn + fp
        fn_rate = fn / total_positives if total_positives > 0 else 0
        fp_rate = fp / total_negatives if total_negatives > 0 else 0

        # Context-specific recommendations
        if self.config.fn_cost_level in ["high", "critical"] and fn_rate > 0.10:
            recommendations.append(
                f"Lower the classification threshold to catch more {self.config.positive_class_meaning.lower()} cases "
                f"(currently missing {fn_rate:.1%})"
            )

        if self.config.fp_cost_level in ["high", "critical"] and fp_rate > 0.10:
            recommendations.append(
                f"Raise the classification threshold to reduce false alarms "
                f"(currently {fp_rate:.1%} false positive rate)"
            )

        if fn > 0 and self.config.fn_cost_level == "critical":
            recommendations.append(
                f"Review the {fn} missed {self.config.positive_class_meaning.lower()} cases to understand patterns"
            )

        if precision < 0.80 and recall < 0.80:
            recommendations.append(
                "Consider collecting more training data or engineering new features"
            )

        if recall > 0.95 and precision < 0.50:
            recommendations.append(
                "Model is over-predicting positives - consider raising threshold or rebalancing training data"
            )

        if precision > 0.95 and recall < 0.50:
            recommendations.append(
                "Model is too conservative - consider lowering threshold or using cost-sensitive learning"
            )

        # Add threshold recommendation from config
        if not recommendations:
            if recall >= 0.90 and precision >= 0.90:
                recommendations.append("Model performance is excellent for this use case")
            else:
                recommendations.append(self.config.threshold_recommendation)

        return recommendations

    def get_summary(self, insight: BusinessInsight) -> str:
        """Generate a human-readable summary of the business insight."""
        risk_indicator = {
            "low": "[OK]",
            "medium": "[WARN]",
            "high": "[HIGH RISK]",
            "critical": "[CRITICAL]"
        }

        lines = [
            "=" * 60,
            f"BUSINESS CONTEXT ANALYSIS: {insight.config.name.upper()}",
            "=" * 60,
            f"Context: {insight.config.description}",
            f"Positive class = {insight.config.positive_class_meaning}",
            f"Negative class = {insight.config.negative_class_meaning}",
            "",
            "CONFUSION MATRIX INTERPRETATION:",
            "-" * 40,
            f"  True Positives:  {insight.true_positives:,} (correctly identified {insight.config.positive_class_meaning.lower()})",
            f"  True Negatives:  {insight.true_negatives:,} (correctly identified {insight.config.negative_class_meaning.lower()})",
            f"  False Positives: {insight.false_positives:,} ({insight.config.fp_description})",
            f"  False Negatives: {insight.false_negatives:,} ({insight.config.fn_description})",
            "",
            "METRICS:",
            "-" * 40,
            f"  Precision: {insight.precision:.1%} (of predicted positives, how many are correct)",
            f"  Recall:    {insight.recall:.1%} (of actual positives, how many did we catch)",
            f"  F1 Score:  {insight.f1_score:.2f}",
            "",
            f"{risk_indicator[insight.risk_level]} RISK LEVEL: {insight.risk_level.upper()}",
            "",
            "ASSESSMENT:",
            "-" * 40,
            f"  {insight.overall_assessment}",
            "",
            f"  False Positives: {insight.fp_interpretation}",
            f"  False Negatives: {insight.fn_interpretation}",
        ]

        if insight.cost_breakdown:
            lines.extend([
                "",
                "COST ANALYSIS:",
                "-" * 40,
                f"  False Positive Cost: ${insight.cost_breakdown['false_positive_cost']:,.2f}",
                f"  False Negative Cost: ${insight.cost_breakdown['false_negative_cost']:,.2f}",
                f"  Total Estimated Cost: ${insight.cost_breakdown['total_cost']:,.2f}",
                f"  Cost per Prediction: ${insight.cost_breakdown['cost_per_prediction']:.2f}",
            ])

        lines.extend([
            "",
            "RECOMMENDATIONS:",
            "-" * 40,
        ])

        for i, rec in enumerate(insight.recommendations, 1):
            lines.append(f"  {i}. {rec}")

        lines.append("=" * 60)

        return "\n".join(lines)

    @staticmethod
    def list_available_contexts() -> List[Dict[str, str]]:
        """List all available business contexts with descriptions."""
        contexts = []
        for context, config in CONTEXT_CONFIGS.items():
            contexts.append({
                "id": context.value,
                "name": config.name,
                "description": config.description,
                "priority_metric": config.priority_metric,
                "fp_cost_level": config.fp_cost_level,
                "fn_cost_level": config.fn_cost_level
            })
        return contexts


@dataclass
class ThresholdResult:
    """Result of threshold optimization."""
    optimal_threshold: float
    default_threshold: float = 0.5
    metric_at_optimal: float = 0.0
    metric_at_default: float = 0.0
    improvement: float = 0.0
    metric_name: str = "f1"


class ThresholdOptimizer:
    """
    Optimizes classification threshold based on business context.

    Different contexts prioritize different metrics:
    - Recall-focused: fraud, medical, churn, quality control
    - Precision-focused: spam, marketing
    - Balanced (F1): loan approval
    """

    def __init__(self, context: BusinessContext):
        """Initialize with a business context."""
        self.context = context
        self.config = CONTEXT_CONFIGS.get(context)
        if not self.config:
            raise ValueError(f"Unknown context: {context}")

    def optimize(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        min_threshold: float = 0.1,
        max_threshold: float = 0.9,
        step: float = 0.01
    ) -> ThresholdResult:
        """
        Find optimal threshold for the business context.

        Args:
            y_true: True labels
            y_proba: Predicted probabilities for positive class
            min_threshold: Minimum threshold to consider
            max_threshold: Maximum threshold to consider
            step: Step size for threshold search

        Returns:
            ThresholdResult with optimal threshold and metrics
        """
        from sklearn.metrics import precision_score, recall_score, f1_score

        thresholds = np.arange(min_threshold, max_threshold + step, step)
        best_threshold = 0.5
        best_score = 0.0
        metric_name = self.config.priority_metric

        for thresh in thresholds:
            y_pred = (y_proba >= thresh).astype(int)

            # Calculate the priority metric
            if metric_name == "recall":
                score = recall_score(y_true, y_pred, zero_division=0)
            elif metric_name == "precision":
                score = precision_score(y_true, y_pred, zero_division=0)
            else:  # f1
                score = f1_score(y_true, y_pred, zero_division=0)

            if score > best_score:
                best_score = score
                best_threshold = thresh

        # Calculate metric at default threshold for comparison
        y_pred_default = (y_proba >= 0.5).astype(int)
        if metric_name == "recall":
            default_score = recall_score(y_true, y_pred_default, zero_division=0)
        elif metric_name == "precision":
            default_score = precision_score(y_true, y_pred_default, zero_division=0)
        else:
            default_score = f1_score(y_true, y_pred_default, zero_division=0)

        improvement = best_score - default_score

        return ThresholdResult(
            optimal_threshold=float(best_threshold),
            default_threshold=0.5,
            metric_at_optimal=float(best_score),
            metric_at_default=float(default_score),
            improvement=float(improvement),
            metric_name=metric_name
        )

    def optimize_with_constraints(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        min_precision: Optional[float] = None,
        min_recall: Optional[float] = None
    ) -> ThresholdResult:
        """
        Find optimal threshold with minimum precision/recall constraints.

        Useful for contexts where you need minimum performance guarantees.

        Args:
            y_true: True labels
            y_proba: Predicted probabilities
            min_precision: Minimum acceptable precision
            min_recall: Minimum acceptable recall

        Returns:
            ThresholdResult respecting constraints
        """
        from sklearn.metrics import precision_score, recall_score, f1_score

        thresholds = np.arange(0.1, 0.91, 0.01)
        best_threshold = 0.5
        best_score = -1.0
        metric_name = self.config.priority_metric

        for thresh in thresholds:
            y_pred = (y_proba >= thresh).astype(int)

            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)

            # Check constraints
            if min_precision is not None and precision < min_precision:
                continue
            if min_recall is not None and recall < min_recall:
                continue

            # Calculate score
            if metric_name == "recall":
                score = recall
            elif metric_name == "precision":
                score = precision
            else:
                score = f1_score(y_true, y_pred, zero_division=0)

            if score > best_score:
                best_score = score
                best_threshold = thresh

        # Fallback if no threshold satisfies constraints
        if best_score < 0:
            return self.optimize(y_true, y_proba)

        y_pred_default = (y_proba >= 0.5).astype(int)
        if metric_name == "recall":
            default_score = recall_score(y_true, y_pred_default, zero_division=0)
        elif metric_name == "precision":
            default_score = precision_score(y_true, y_pred_default, zero_division=0)
        else:
            default_score = f1_score(y_true, y_pred_default, zero_division=0)

        return ThresholdResult(
            optimal_threshold=float(best_threshold),
            default_threshold=0.5,
            metric_at_optimal=float(best_score),
            metric_at_default=float(default_score),
            improvement=float(best_score - default_score),
            metric_name=metric_name
        )


def get_scoring_metric(context: BusinessContext) -> str:
    """
    Get the sklearn scoring metric name for a business context.

    Returns the metric to use for model selection during cross-validation.
    """
    config = CONTEXT_CONFIGS.get(context)
    if not config:
        return "f1"

    metric_map = {
        "recall": "recall",
        "precision": "precision",
        "f1": "f1"
    }
    return metric_map.get(config.priority_metric, "f1")
