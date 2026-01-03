from sklearn.model_selection import StratifiedKFold
import numpy as np

def optimize_threshold_cv(model, X, y_true, metric, cv=5, random_state=None):
    """
    Finds the optimal threshold by cross-validation.

    Args:
        model: sklearn-like estimator (non fitato)
        X: features
        y_true: labels
        metric: function metric(y_true, y_pred)
        cv: number of folds or cross-validation splitter
        random_state: for reproducibility

    Returns:
        mean_best_threshold: mean of best thresholds across folds
        mean_best_metric: mean of metric values across folds
    """
    if isinstance(cv, int):
        cv = StratifiedKFold(n_splits=cv, shuffle=True, random_state=random_state)

    best_thresholds = []
    best_metrics = []

    for train_idx, val_idx in cv.split(X, y_true):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y_true[train_idx], y_true[val_idx]

        # Clone model to avoid leakage
        from sklearn.base import clone
        if not (hasattr(model, "predict_proba") or hasattr(model, "decision_function")):
            raise ValueError("Model must implement predict_proba or decision_function")

        clf = clone(model)
        clf.fit(X_train, y_train)

        # Ottieni probabilità o score
        if hasattr(clf, "predict_proba"):
            y_scores = clf.predict_proba(X_val)[:, 1]
        elif hasattr(clf, "decision_function"):
            y_scores = clf.decision_function(X_val)
            # Normalizza in [0,1]
            y_scores = (y_scores - y_scores.min()) / (y_scores.max() - y_scores.min())
        else:
            raise ValueError("Model has neither predict_proba nor decision_function")

        # Cerca soglia che massimizza la metrica
        thresholds = np.unique(y_scores)
        best_thresh = 0.5
        best_metric_val = -np.inf

        for thresh in thresholds:
            y_pred = (y_scores >= thresh).astype(int)
            val = metric(y_val, y_pred)
            if val > best_metric_val:
                best_metric_val = val
                best_thresh = thresh

        best_thresholds.append(best_thresh)
        best_metrics.append(best_metric_val)

    mean_best_threshold = np.mean(best_thresholds)
    mean_best_metric = np.mean(best_metrics)

    return mean_best_threshold, mean_best_metric
