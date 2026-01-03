"""
Business Report Module

Translates technical ML metrics into business-friendly language.
Provides actionable insights for non-technical stakeholders.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import numpy as np


class ModelQuality(Enum):
    """Overall model quality assessment."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


@dataclass
class BusinessMetricExplanation:
    """Business-friendly explanation of a metric."""
    metric_name: str
    technical_name: str
    value: float
    plain_english: str
    business_impact: str
    recommendation: Optional[str] = None
    quality: ModelQuality = ModelQuality.ACCEPTABLE


@dataclass
class ClassPredictionMeaning:
    """Explains what each predicted class means."""
    class_label: Any
    class_name: str
    description: str
    action_required: str
    priority: str  # "high", "medium", "low"
    actual_value: Optional[str] = None  # The actual target value from dataset (e.g., ">50K")


@dataclass
class PredictionExplanation:
    """Business-friendly explanation of a single prediction."""
    predicted_class: Any
    class_meaning: str
    confidence: float
    confidence_level: str  # "high", "medium", "low"
    recommendation: str
    risk_level: str  # "high", "medium", "low"


@dataclass
class PredictionReport:
    """Complete business report for predictions."""
    total_predictions: int
    class_distribution: Dict[Any, int]
    class_meanings: Dict[Any, ClassPredictionMeaning]
    summary: str
    action_items: List[str]
    high_priority_count: int
    predictions_with_explanations: List[PredictionExplanation] = field(default_factory=list)


@dataclass
class BusinessReport:
    """Complete business-friendly model report."""
    executive_summary: str
    model_quality: ModelQuality
    quality_score: int  # 0-100
    key_findings: List[str]
    metric_explanations: List[BusinessMetricExplanation]
    recommendations: List[str]
    limitations: List[str]
    class_meanings: Optional[Dict[Any, ClassPredictionMeaning]] = None


class BusinessReportGenerator:
    """
    Generates business-friendly reports from ML metrics.
    Translates technical jargon into actionable insights.
    """

    # Thresholds for quality assessment
    THRESHOLDS = {
        'accuracy': {'excellent': 0.95, 'good': 0.85, 'acceptable': 0.75, 'poor': 0.60},
        'precision': {'excellent': 0.95, 'good': 0.85, 'acceptable': 0.70, 'poor': 0.50},
        'recall': {'excellent': 0.95, 'good': 0.85, 'acceptable': 0.70, 'poor': 0.50},
        'f1': {'excellent': 0.95, 'good': 0.85, 'acceptable': 0.70, 'poor': 0.50},
        'roc_auc': {'excellent': 0.95, 'good': 0.85, 'acceptable': 0.70, 'poor': 0.55},
        'r2': {'excellent': 0.90, 'good': 0.75, 'acceptable': 0.50, 'poor': 0.25},
    }

    # Business context definitions for class meanings
    DEFAULT_CLASS_MEANINGS = {
        # Binary classification defaults
        0: ClassPredictionMeaning(
            class_label=0,
            class_name="Negative / No",
            description="The model predicts this case belongs to the negative class",
            action_required="Standard processing - no special action needed",
            priority="low"
        ),
        1: ClassPredictionMeaning(
            class_label=1,
            class_name="Positive / Yes",
            description="The model predicts this case belongs to the positive class",
            action_required="Review recommended - may require attention",
            priority="medium"
        )
    }

    # Context-specific class meanings
    CONTEXT_CLASS_MEANINGS = {
        'fraud_detection': {
            0: ClassPredictionMeaning(0, "Legitimate", "Transaction appears to be legitimate", "Process normally", "low"),
            1: ClassPredictionMeaning(1, "Potential Fraud", "Transaction flagged as potentially fraudulent", "Block and investigate immediately", "high")
        },
        'churn_prediction': {
            0: ClassPredictionMeaning(0, "Likely to Stay", "Customer is predicted to remain active", "Standard engagement", "low"),
            1: ClassPredictionMeaning(1, "Churn Risk", "Customer is at risk of leaving", "Initiate retention campaign immediately", "high")
        },
        'medical_diagnosis': {
            0: ClassPredictionMeaning(0, "Negative", "No indication of condition detected", "Continue routine monitoring", "low"),
            1: ClassPredictionMeaning(1, "Positive", "Possible condition detected", "Schedule follow-up examination immediately", "high")
        },
        'spam_detection': {
            0: ClassPredictionMeaning(0, "Legitimate", "Message appears to be legitimate", "Deliver to inbox", "low"),
            1: ClassPredictionMeaning(1, "Spam", "Message identified as spam", "Move to spam folder", "medium")
        },
        'loan_approval': {
            0: ClassPredictionMeaning(0, "Low Risk", "Applicant has good credit profile", "Approve with standard terms", "low"),
            1: ClassPredictionMeaning(1, "High Risk / Default", "Applicant may default on loan", "Decline or require additional verification", "high")
        },
        'marketing_campaign': {
            0: ClassPredictionMeaning(0, "Unlikely to Respond", "Customer unlikely to respond to campaign", "Exclude from campaign", "low"),
            1: ClassPredictionMeaning(1, "Likely to Respond", "Customer likely to respond positively", "Include in campaign priority list", "medium")
        },
        'quality_control': {
            0: ClassPredictionMeaning(0, "Pass", "Product meets quality standards", "Continue to shipping", "low"),
            1: ClassPredictionMeaning(1, "Defect", "Product has potential quality issues", "Remove from line for inspection", "high")
        }
    }

    def __init__(self, context: Optional[str] = None):
        """
        Initialize the report generator.

        Args:
            context: Business context (e.g., 'fraud_detection', 'loan_approval')
        """
        self.context = context

        # Set class meanings based on context
        if context and context in self.CONTEXT_CLASS_MEANINGS:
            self.class_meanings = self.CONTEXT_CLASS_MEANINGS[context]
        else:
            self.class_meanings = self.DEFAULT_CLASS_MEANINGS.copy()

    def set_class_meanings(self, meanings: Dict[Any, ClassPredictionMeaning]):
        """Override class meanings with custom definitions."""
        self.class_meanings = meanings

    def _get_quality(self, metric: str, value: float) -> ModelQuality:
        """Determine quality level for a metric value."""
        thresholds = self.THRESHOLDS.get(metric, self.THRESHOLDS['f1'])

        if value >= thresholds['excellent']:
            return ModelQuality.EXCELLENT
        elif value >= thresholds['good']:
            return ModelQuality.GOOD
        elif value >= thresholds['acceptable']:
            return ModelQuality.ACCEPTABLE
        elif value >= thresholds['poor']:
            return ModelQuality.NEEDS_IMPROVEMENT
        else:
            return ModelQuality.POOR

    def _explain_accuracy(self, value: float) -> BusinessMetricExplanation:
        """Explain accuracy in business terms."""
        pct = value * 100
        quality = self._get_quality('accuracy', value)

        plain_english = f"The model correctly predicts {pct:.1f}% of all cases."

        if value >= 0.95:
            business_impact = "Excellent reliability - very few errors expected in production."
            recommendation = None
        elif value >= 0.85:
            business_impact = f"Good reliability - expect about {100-pct:.0f} errors per 100 predictions."
            recommendation = None
        elif value >= 0.75:
            business_impact = f"Acceptable reliability - expect about {100-pct:.0f} errors per 100 predictions. Human review recommended for critical decisions."
            recommendation = "Consider adding manual review for high-stakes decisions."
        else:
            business_impact = f"Low reliability - {100-pct:.0f}% of predictions may be wrong."
            recommendation = "Model needs improvement before production use. Consider more training data or feature engineering."

        return BusinessMetricExplanation(
            metric_name="Overall Accuracy",
            technical_name="accuracy",
            value=value,
            plain_english=plain_english,
            business_impact=business_impact,
            recommendation=recommendation,
            quality=quality
        )

    def _explain_precision(self, value: float) -> BusinessMetricExplanation:
        """Explain precision in business terms."""
        pct = value * 100
        quality = self._get_quality('precision', value)

        plain_english = f"When the model predicts 'Yes/Positive', it is correct {pct:.1f}% of the time."

        context_examples = {
            'fraud_detection': f"Out of 100 transactions flagged as fraud, {pct:.0f} are actually fraudulent.",
            'churn_prediction': f"Out of 100 customers predicted to churn, {pct:.0f} actually leave.",
            'loan_approval': f"Out of 100 applications flagged as risky, {pct:.0f} would actually default.",
            'spam_detection': f"Out of 100 emails marked as spam, {pct:.0f} are actually spam.",
        }

        if self.context and self.context in context_examples:
            plain_english = context_examples[self.context]

        false_positive_rate = 100 - pct
        if value >= 0.90:
            business_impact = f"Very few false alarms - only {false_positive_rate:.0f}% of positive predictions are wrong."
        elif value >= 0.75:
            business_impact = f"Some false alarms expected - {false_positive_rate:.0f}% of positive predictions are incorrect."
            recommendation = "Consider reviewing positive predictions before taking action."
        else:
            business_impact = f"High false alarm rate - {false_positive_rate:.0f}% of 'positive' predictions are actually negative."
            recommendation = "Too many false positives. Manual verification strongly recommended."

        return BusinessMetricExplanation(
            metric_name="Precision (False Alarm Rate)",
            technical_name="precision",
            value=value,
            plain_english=plain_english,
            business_impact=business_impact,
            recommendation=recommendation if value < 0.90 else None,
            quality=quality
        )

    def _explain_recall(self, value: float) -> BusinessMetricExplanation:
        """Explain recall in business terms."""
        pct = value * 100
        quality = self._get_quality('recall', value)

        plain_english = f"The model catches {pct:.1f}% of all actual positive cases."

        context_examples = {
            'fraud_detection': f"The model detects {pct:.0f}% of all actual fraud cases. {100-pct:.0f}% of fraud goes undetected.",
            'churn_prediction': f"The model identifies {pct:.0f}% of customers who will actually churn. {100-pct:.0f}% are missed.",
            'medical_diagnosis': f"The model detects {pct:.0f}% of all actual positive cases. {100-pct:.0f}% may be missed.",
            'quality_control': f"The model catches {pct:.0f}% of all defective products. {100-pct:.0f}% of defects may slip through.",
        }

        if self.context and self.context in context_examples:
            plain_english = context_examples[self.context]

        missed_rate = 100 - pct
        if value >= 0.95:
            business_impact = f"Excellent detection rate - only {missed_rate:.1f}% of positive cases are missed."
        elif value >= 0.85:
            business_impact = f"Good detection rate - about {missed_rate:.0f}% of positive cases may be missed."
        elif value >= 0.70:
            business_impact = f"Moderate detection rate - {missed_rate:.0f}% of positive cases are not detected."
            recommendation = "Consider adjusting the model threshold to catch more cases."
        else:
            business_impact = f"Low detection rate - {missed_rate:.0f}% of actual positive cases are missed."
            recommendation = "Model is missing too many cases. Consider threshold adjustment or model retraining."

        return BusinessMetricExplanation(
            metric_name="Recall (Detection Rate)",
            technical_name="recall",
            value=value,
            plain_english=plain_english,
            business_impact=business_impact,
            recommendation=recommendation if value < 0.85 else None,
            quality=quality
        )

    def _explain_f1(self, value: float) -> BusinessMetricExplanation:
        """Explain F1 score in business terms."""
        pct = value * 100
        quality = self._get_quality('f1', value)

        plain_english = f"The model achieves {pct:.1f}% balanced performance between catching positives and avoiding false alarms."

        if value >= 0.90:
            business_impact = "Excellent balance between detection and precision."
        elif value >= 0.80:
            business_impact = "Good overall performance with reasonable balance."
        elif value >= 0.70:
            business_impact = "Acceptable performance but may need optimization for your specific use case."
        else:
            business_impact = "Performance needs improvement. Consider focusing on either precision or recall based on business needs."

        return BusinessMetricExplanation(
            metric_name="Balanced Performance Score",
            technical_name="f1",
            value=value,
            plain_english=plain_english,
            business_impact=business_impact,
            quality=quality
        )

    def _explain_roc_auc(self, value: float) -> BusinessMetricExplanation:
        """Explain ROC-AUC in business terms."""
        quality = self._get_quality('roc_auc', value)

        if value >= 0.90:
            plain_english = "The model has excellent ability to distinguish between positive and negative cases."
            business_impact = "Very reliable ranking - top-ranked predictions are highly likely to be correct."
        elif value >= 0.80:
            plain_english = "The model has good ability to rank and separate positive from negative cases."
            business_impact = "Good ranking ability - useful for prioritizing cases for review."
        elif value >= 0.70:
            plain_english = "The model has moderate ability to distinguish between classes."
            business_impact = "Acceptable for initial screening but should not be sole decision factor."
        elif value >= 0.60:
            plain_english = "The model has weak discriminative ability."
            business_impact = "Limited usefulness - barely better than random ranking."
        else:
            plain_english = "The model performs close to random chance."
            business_impact = "Not suitable for production use."

        return BusinessMetricExplanation(
            metric_name="Discrimination Ability",
            technical_name="roc_auc",
            value=value,
            plain_english=plain_english,
            business_impact=business_impact,
            quality=quality
        )

    def _explain_r2(self, value: float) -> BusinessMetricExplanation:
        """Explain R² for regression in business terms."""
        pct = value * 100
        quality = self._get_quality('r2', value)

        plain_english = f"The model explains {pct:.1f}% of the variation in the target variable."

        if value >= 0.90:
            business_impact = "Excellent fit - predictions are very close to actual values."
        elif value >= 0.75:
            business_impact = "Good fit - model captures most of the patterns in the data."
        elif value >= 0.50:
            business_impact = "Moderate fit - model provides useful predictions but with noticeable error."
            recommendation = "Consider adding more features or using a more complex model."
        else:
            business_impact = "Weak fit - model predictions have significant error."
            recommendation = "Model needs substantial improvement. Consider feature engineering or alternative approaches."

        return BusinessMetricExplanation(
            metric_name="Prediction Accuracy (R²)",
            technical_name="r2",
            value=value,
            plain_english=plain_english,
            business_impact=business_impact,
            recommendation=recommendation if value < 0.75 else None,
            quality=quality
        )

    def _explain_rmse(self, value: float, target_range: Tuple[float, float] = None) -> BusinessMetricExplanation:
        """Explain RMSE in business terms."""
        plain_english = f"On average, predictions are off by about {value:.2f} units."

        if target_range:
            range_size = target_range[1] - target_range[0]
            error_pct = (value / range_size) * 100
            plain_english += f" This represents about {error_pct:.1f}% of the typical value range."

            if error_pct <= 5:
                business_impact = "Very accurate predictions - errors are small relative to the values."
                quality = ModelQuality.EXCELLENT
            elif error_pct <= 10:
                business_impact = "Good prediction accuracy with acceptable error margins."
                quality = ModelQuality.GOOD
            elif error_pct <= 20:
                business_impact = "Moderate accuracy - consider error margins in decision making."
                quality = ModelQuality.ACCEPTABLE
            else:
                business_impact = "High prediction error - use with caution."
                quality = ModelQuality.NEEDS_IMPROVEMENT
        else:
            business_impact = "Review this value in context of your target variable's typical values."
            quality = ModelQuality.ACCEPTABLE

        return BusinessMetricExplanation(
            metric_name="Average Prediction Error",
            technical_name="rmse",
            value=value,
            plain_english=plain_english,
            business_impact=business_impact,
            quality=quality
        )

    def _explain_mae(self, value: float) -> BusinessMetricExplanation:
        """Explain MAE in business terms."""
        plain_english = f"On average, predictions differ from actual values by {value:.2f} units."
        business_impact = "This is the typical error you can expect for any single prediction."

        return BusinessMetricExplanation(
            metric_name="Typical Prediction Error",
            technical_name="mae",
            value=value,
            plain_english=plain_english,
            business_impact=business_impact,
            quality=ModelQuality.ACCEPTABLE
        )

    def generate_report(
        self,
        metrics: Dict[str, float],
        task_type: str,
        model_name: str,
        class_labels: Optional[List[Any]] = None
    ) -> BusinessReport:
        """
        Generate a complete business-friendly report.

        Args:
            metrics: Dictionary of metric names to values
            task_type: 'classification' or 'regression'
            model_name: Name of the model
            class_labels: Optional list of class labels for classification

        Returns:
            BusinessReport with all explanations
        """
        explanations = []
        recommendations = []
        key_findings = []

        is_classification = 'classification' in task_type.lower()

        # Generate explanations for each metric
        if is_classification:
            if 'accuracy' in metrics:
                exp = self._explain_accuracy(metrics['accuracy'])
                explanations.append(exp)
                if exp.recommendation:
                    recommendations.append(exp.recommendation)

            if 'precision' in metrics:
                exp = self._explain_precision(metrics['precision'])
                explanations.append(exp)
                if exp.recommendation:
                    recommendations.append(exp.recommendation)

            if 'recall' in metrics:
                exp = self._explain_recall(metrics['recall'])
                explanations.append(exp)
                if exp.recommendation:
                    recommendations.append(exp.recommendation)

            if 'f1' in metrics:
                exp = self._explain_f1(metrics['f1'])
                explanations.append(exp)
                if exp.recommendation:
                    recommendations.append(exp.recommendation)

            if 'roc_auc' in metrics:
                exp = self._explain_roc_auc(metrics['roc_auc'])
                explanations.append(exp)
                if exp.recommendation:
                    recommendations.append(exp.recommendation)
        else:
            # Regression metrics
            if 'r2' in metrics:
                exp = self._explain_r2(metrics['r2'])
                explanations.append(exp)
                if exp.recommendation:
                    recommendations.append(exp.recommendation)

            if 'rmse' in metrics:
                exp = self._explain_rmse(metrics['rmse'])
                explanations.append(exp)
                if exp.recommendation:
                    recommendations.append(exp.recommendation)

            if 'mae' in metrics:
                exp = self._explain_mae(metrics['mae'])
                explanations.append(exp)

        # Determine overall quality
        qualities = [exp.quality for exp in explanations]
        quality_scores = {
            ModelQuality.EXCELLENT: 100,
            ModelQuality.GOOD: 80,
            ModelQuality.ACCEPTABLE: 60,
            ModelQuality.NEEDS_IMPROVEMENT: 40,
            ModelQuality.POOR: 20
        }

        avg_score = np.mean([quality_scores[q] for q in qualities]) if qualities else 50

        if avg_score >= 90:
            overall_quality = ModelQuality.EXCELLENT
        elif avg_score >= 75:
            overall_quality = ModelQuality.GOOD
        elif avg_score >= 55:
            overall_quality = ModelQuality.ACCEPTABLE
        elif avg_score >= 35:
            overall_quality = ModelQuality.NEEDS_IMPROVEMENT
        else:
            overall_quality = ModelQuality.POOR

        # Generate executive summary
        quality_descriptions = {
            ModelQuality.EXCELLENT: "is performing excellently and is ready for production use",
            ModelQuality.GOOD: "is performing well and suitable for production with monitoring",
            ModelQuality.ACCEPTABLE: "has acceptable performance but should be monitored closely",
            ModelQuality.NEEDS_IMPROVEMENT: "needs improvement before production deployment",
            ModelQuality.POOR: "is not performing adequately and requires significant work"
        }

        executive_summary = f"The {model_name} model {quality_descriptions[overall_quality]}."

        if is_classification:
            if 'accuracy' in metrics:
                key_findings.append(f"Overall accuracy: {metrics['accuracy']*100:.1f}% of predictions are correct")
            if 'precision' in metrics and 'recall' in metrics:
                key_findings.append(f"Detection rate: Catches {metrics['recall']*100:.0f}% of positive cases")
                key_findings.append(f"False alarm rate: {(1-metrics['precision'])*100:.0f}% of positive predictions are incorrect")
        else:
            if 'r2' in metrics:
                key_findings.append(f"Model explains {metrics['r2']*100:.1f}% of the variation in the data")
            if 'mae' in metrics:
                key_findings.append(f"Typical prediction error: ±{metrics['mae']:.2f} units")

        # Standard limitations
        limitations = [
            "Model performance is based on historical data and may not reflect future patterns",
            "Unusual or edge cases may not be well predicted",
            "Regular monitoring and retraining is recommended"
        ]

        if overall_quality in [ModelQuality.NEEDS_IMPROVEMENT, ModelQuality.POOR]:
            limitations.append("Consider collecting more training data or engineering new features")

        # Set class meanings for classification
        class_meanings = None
        if is_classification and class_labels:
            class_meanings = {}
            # Sort labels to match LabelEncoder behavior (alphabetical order)
            sorted_labels = sorted([str(l) for l in class_labels])

            for idx, label in enumerate(class_labels):
                str_label = str(label)
                # Determine encoded position (0 or 1 for binary) based on sorted order
                encoded_idx = sorted_labels.index(str_label) if str_label in sorted_labels else idx

                # Check if we have context-specific meanings for the encoded index
                if encoded_idx in self.class_meanings and self.context:
                    # Use context-specific meaning but with actual label
                    base_meaning = self.class_meanings[encoded_idx]
                    class_meanings[label] = ClassPredictionMeaning(
                        class_label=label,
                        class_name=base_meaning.class_name,
                        description=base_meaning.description,
                        action_required=base_meaning.action_required,
                        priority=base_meaning.priority,
                        actual_value=str_label
                    )
                else:
                    # No specific context - use actual label as the class name
                    # For binary, first alphabetically is typically "negative" (0), second is "positive" (1)
                    if len(class_labels) == 2:
                        if encoded_idx == 0:
                            priority = "low"
                            description = f"Model predicts: {str_label}"
                            action = "Standard processing - no special action needed"
                        else:
                            priority = "medium"
                            description = f"Model predicts: {str_label}"
                            action = "Review recommended - may require attention"
                    else:
                        priority = "medium"
                        description = f"Model predicts: {str_label}"
                        action = "Process according to business rules"

                    class_meanings[label] = ClassPredictionMeaning(
                        class_label=label,
                        class_name=str_label,  # Use actual label as the display name
                        description=description,
                        action_required=action,
                        priority=priority,
                        actual_value=str_label
                    )

        return BusinessReport(
            executive_summary=executive_summary,
            model_quality=overall_quality,
            quality_score=int(avg_score),
            key_findings=key_findings,
            metric_explanations=explanations,
            recommendations=recommendations if recommendations else ["No immediate action required - model is performing well."],
            limitations=limitations,
            class_meanings=class_meanings
        )

    def explain_prediction(
        self,
        prediction: Any,
        probability: Optional[float] = None,
        threshold: float = 0.5
    ) -> PredictionExplanation:
        """
        Generate business explanation for a single prediction.

        Args:
            prediction: The predicted class/value
            probability: Confidence probability (0-1)
            threshold: Decision threshold used

        Returns:
            PredictionExplanation with business context
        """
        # Get class meaning
        if prediction in self.class_meanings:
            meaning = self.class_meanings[prediction]
            class_meaning = meaning.description
            recommendation = meaning.action_required
            risk_level = meaning.priority
        else:
            class_meaning = f"Predicted: {prediction}"
            recommendation = "Review this prediction based on business rules"
            risk_level = "medium"

        # Determine confidence level
        if probability is not None:
            # Distance from threshold indicates confidence
            confidence = max(probability, 1 - probability)
            if confidence >= 0.90:
                confidence_level = "high"
            elif confidence >= 0.70:
                confidence_level = "medium"
            else:
                confidence_level = "low"
        else:
            confidence = 1.0
            confidence_level = "unknown"

        return PredictionExplanation(
            predicted_class=prediction,
            class_meaning=class_meaning,
            confidence=confidence,
            confidence_level=confidence_level,
            recommendation=recommendation,
            risk_level=risk_level
        )

    def generate_prediction_report(
        self,
        predictions: np.ndarray,
        probabilities: Optional[np.ndarray] = None,
        class_labels: Optional[List[Any]] = None
    ) -> PredictionReport:
        """
        Generate a business-friendly report for batch predictions.

        Args:
            predictions: Array of predictions
            probabilities: Optional probability array
            class_labels: Optional list of class labels

        Returns:
            PredictionReport with summary and action items
        """
        total = len(predictions)

        # Count predictions per class
        unique, counts = np.unique(predictions, return_counts=True)
        class_distribution = dict(zip(unique.tolist(), counts.tolist()))

        # Build class meanings
        class_meanings = {}
        for label in unique:
            if label in self.class_meanings:
                class_meanings[label] = self.class_meanings[label]
            else:
                class_meanings[label] = ClassPredictionMeaning(
                    class_label=label,
                    class_name=str(label),
                    description=f"Class {label}",
                    action_required="Process according to business rules",
                    priority="medium"
                )

        # Count high priority items
        high_priority_count = sum(
            count for label, count in class_distribution.items()
            if label in class_meanings and class_meanings[label].priority == "high"
        )

        # Generate summary
        summary_parts = [f"Processed {total:,} predictions."]
        for label, count in sorted(class_distribution.items(), key=lambda x: -x[1]):
            pct = (count / total) * 100
            class_name = class_meanings[label].class_name if label in class_meanings else str(label)
            summary_parts.append(f"  • {class_name}: {count:,} ({pct:.1f}%)")

        summary = "\n".join(summary_parts)

        # Generate action items
        action_items = []
        for label, meaning in class_meanings.items():
            if label in class_distribution:
                count = class_distribution[label]
                if meaning.priority == "high" and count > 0:
                    action_items.append(f"URGENT: {count:,} cases require immediate attention - {meaning.action_required}")
                elif meaning.priority == "medium" and count > 0:
                    action_items.append(f"ACTION: {count:,} cases need review - {meaning.action_required}")

        if not action_items:
            action_items.append("No urgent action items identified.")

        # Generate individual explanations (for first 100)
        explanations = []
        for i, pred in enumerate(predictions[:100]):
            prob = probabilities[i] if probabilities is not None else None
            if prob is not None and len(prob) > 1:
                prob = max(prob)  # Get max probability
            explanations.append(self.explain_prediction(pred, prob))

        return PredictionReport(
            total_predictions=total,
            class_distribution=class_distribution,
            class_meanings=class_meanings,
            summary=summary,
            action_items=action_items,
            high_priority_count=high_priority_count,
            predictions_with_explanations=explanations
        )


def format_business_report_text(report: BusinessReport) -> str:
    """Format a BusinessReport as plain text."""
    lines = [
        "=" * 60,
        "BUSINESS MODEL REPORT",
        "=" * 60,
        "",
        "EXECUTIVE SUMMARY",
        "-" * 40,
        report.executive_summary,
        f"",
        f"Overall Quality Score: {report.quality_score}/100 ({report.model_quality.value.upper()})",
        "",
        "KEY FINDINGS",
        "-" * 40,
    ]

    for finding in report.key_findings:
        lines.append(f"  • {finding}")

    lines.extend([
        "",
        "DETAILED METRICS",
        "-" * 40,
    ])

    for exp in report.metric_explanations:
        lines.append(f"\n{exp.metric_name} ({exp.technical_name}): {exp.value:.4f}")
        lines.append(f"  What it means: {exp.plain_english}")
        lines.append(f"  Business impact: {exp.business_impact}")
        if exp.recommendation:
            lines.append(f"  Recommendation: {exp.recommendation}")

    lines.extend([
        "",
        "RECOMMENDATIONS",
        "-" * 40,
    ])

    for rec in report.recommendations:
        lines.append(f"  • {rec}")

    if report.class_meanings:
        lines.extend([
            "",
            "PREDICTION CLASS MEANINGS",
            "-" * 40,
        ])
        # Sort labels to determine encoded class index
        sorted_labels = sorted([str(l) for l in report.class_meanings.keys()])
        for label, meaning in report.class_meanings.items():
            display_value = meaning.actual_value if meaning.actual_value else str(label)
            encoded_idx = sorted_labels.index(str(label)) if str(label) in sorted_labels else "?"
            lines.append(f"\n  Class {encoded_idx} → '{display_value}' - {meaning.class_name}")
            lines.append(f"    {meaning.description}")
            lines.append(f"    Action: {meaning.action_required}")
            lines.append(f"    Priority: {meaning.priority.upper()}")

    lines.extend([
        "",
        "LIMITATIONS",
        "-" * 40,
    ])

    for limit in report.limitations:
        lines.append(f"  • {limit}")

    lines.append("=" * 60)

    return "\n".join(lines)


def format_prediction_report_text(report: PredictionReport) -> str:
    """Format a PredictionReport as plain text."""
    lines = [
        "=" * 60,
        "PREDICTION REPORT",
        "=" * 60,
        "",
        "SUMMARY",
        "-" * 40,
        report.summary,
        "",
    ]

    if report.high_priority_count > 0:
        lines.extend([
            f"⚠️  HIGH PRIORITY: {report.high_priority_count:,} items require immediate attention",
            ""
        ])

    lines.extend([
        "ACTION ITEMS",
        "-" * 40,
    ])

    for action in report.action_items:
        lines.append(f"  • {action}")

    lines.extend([
        "",
        "CLASS MEANINGS",
        "-" * 40,
    ])

    for label, meaning in report.class_meanings.items():
        lines.append(f"  {meaning.class_name} (Class {label}): {meaning.description}")

    lines.append("=" * 60)

    return "\n".join(lines)
