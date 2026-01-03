"""
core.py - Facade module for threshopt library
Provides a single interface for optimizing thresholds,
plotting probability distributions, and displaying confusion matrices.
"""

# -----------------------------
# Import functions from submodules
# -----------------------------
from .thresholds import best_threshold_binary, best_threshold_multiclass
from .plotting import plot_probability_distribution, plot_confusion_matrix_custom
from .utils import sigmoid, softmax, validate_inputs

# -----------------------------
# Main facade function
# -----------------------------
def optimize_threshold(model, X, y_true, metric, multiclass=False,
                       use_predict_if_no_proba=False, plot=True, cm=True, report=True):
    """
    Main facade function to optimize classification thresholds,
    optionally plot probability distributions and display confusion matrices.

    Args:
        model: trained classifier (with predict_proba, decision_function, or predict)
        X: array-like of features
        y_true: array-like of true labels
        metric: function(y_true, y_pred) -> float, metric to optimize
        multiclass: bool, if True performs One-vs-Rest threshold optimization
        use_predict_if_no_proba: bool, fallback to predict() if no probability scores
        plot: bool, if True plots probability distributions
        cm: bool, if True displays confusion matrix
        report: bool, if True prints classification report

    Returns:
        thresholds: optimal threshold(s), scalar for binary, array for multiclass
        best_scores: corresponding metric value(s)
    """

    # -----------------------------
    # Get probabilistic scores from the model
    # -----------------------------
    if hasattr(model, "predict_proba"):
        y_scores = model.predict_proba(X)
    elif hasattr(model, "decision_function"):
        y_scores = model.decision_function(X)
    else:
        raise ValueError("Model must implement predict_proba or decision_function")
    y_true, y_scores = validate_inputs(y_true, y_scores)

    if not multiclass:
        if y_scores.ndim == 2:
            y_scores = y_scores[:, 1]

    # -----------------------------
    # Compute optimal thresholds
    # -----------------------------
    if multiclass:
        thresholds, best_scores = best_threshold_multiclass(y_true, y_scores, metric)
    else:
        thresholds, best_scores = best_threshold_binary(y_true, y_scores, metric)

    # -----------------------------
    # Plot probability distributions if requested
    # -----------------------------
    if plot:
        plot_probability_distribution(y_true, y_scores, thresholds)

    # -----------------------------
    # Plot confusion matrix and optionally print classification report
    # -----------------------------
    if cm:
        plot_confusion_matrix_custom(y_true, y_scores, thresholds, report)

    return thresholds, best_scores
