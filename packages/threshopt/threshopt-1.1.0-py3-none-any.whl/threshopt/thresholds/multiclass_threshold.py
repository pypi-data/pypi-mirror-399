import numpy as np
from .binary_threshold import best_threshold_binary

def best_threshold_multiclass(y_true, y_scores, metric):
    """
    Calculate optimal One-vs-Rest thresholds for multiclass classification.
    """
    classes = np.unique(y_true)
    n_classes = y_scores.shape[1]
    thresholds = np.zeros(n_classes)
    best_scores = np.zeros(n_classes)
    for k in range(n_classes):
        y_bin = (y_true == classes[k]).astype(int)
        t, s = best_threshold_binary(y_bin, y_scores[:, k], metric)
        thresholds[k] = t
        best_scores[k] = s
    return thresholds, best_scores
