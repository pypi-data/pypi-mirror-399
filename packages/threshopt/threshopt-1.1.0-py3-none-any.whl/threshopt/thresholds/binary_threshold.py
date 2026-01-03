import numpy as np

def best_threshold_binary(y_true, y_prob, metric):
    """
    Calculate the optimal threshold for a binary classifier.
    """
    thresholds = np.linspace(0, 1, 200)
    best_score = -np.inf
    best_t = 0.5
    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        try:
            score = metric(y_true, y_pred)
        except ZeroDivisionError:
            score = 0
        if score > best_score:
            best_score = score
            best_t = t
    return best_t, best_score
