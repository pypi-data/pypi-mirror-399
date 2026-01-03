from sklearn.metrics import confusion_matrix, balanced_accuracy_score
import numpy as np

def gmean_score(y_true, y_pred):
    """
    Geometric Mean of sensitivity and specificity.
    """
    cm = confusion_matrix(y_true, y_pred, labels=[0,1])

    tn, fp, fn, tp = cm.ravel()

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

    return np.sqrt(sensitivity * specificity)


def youden_j_stat(y_true, y_pred):
    """
    Youden's J statistic = sensitivity + specificity - 1
    """
    cm = confusion_matrix(y_true, y_pred, labels=[0,1])
    tn, fp, fn, tp = cm.ravel()

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

    return sensitivity + specificity - 1


def balanced_acc_score(y_true, y_pred):
    """
    Balanced accuracy (wrapper sklearn for convenience)
    """
    return balanced_accuracy_score(y_true, y_pred)
