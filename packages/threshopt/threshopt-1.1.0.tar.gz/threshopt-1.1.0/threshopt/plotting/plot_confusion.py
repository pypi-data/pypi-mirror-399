from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report
import matplotlib.pyplot as plt
import numpy as np

def plot_confusion_matrix_custom(y_true, y_scores, thresholds, report=True, show=True):
    classes = np.unique(y_true)
    
    # Automatically determine mode based on the dimensions of y_scores
    if y_scores.ndim == 1:
        # Binary classification mode, only probabilities for positive class
        y_pred = (y_scores >= thresholds).astype(int)
        if report:
            print(classification_report(y_true, y_pred))
        cmatrix = confusion_matrix(y_true, y_pred)
        disp = ConfusionMatrixDisplay(cmatrix, display_labels=classes)
        disp.plot(cmap=plt.cm.Greens)
        if show:
            plt.show()
            
    elif y_scores.shape[1] == 2:
        # Binary classification mode, probabilities for both classes
        y_pred = (y_scores[:, 1] >= thresholds).astype(int)
        if report:
            print(classification_report(y_true, y_pred))
        cmatrix = confusion_matrix(y_true, y_pred)
        disp = ConfusionMatrixDisplay(cmatrix, display_labels=classes)
        disp.plot(cmap=plt.cm.Greens)
        if show:
            plt.show()
            
    else:
        # Multi-class classification mode
        for k, cls in enumerate(classes):
            y_pred_k = (y_scores[:, k] >= thresholds[k]).astype(int)
            y_bin = (y_true == cls).astype(int)
            if report:
                print(f"Class {cls}")
                print(classification_report(y_bin, y_pred_k))
            cmatrix = confusion_matrix(y_bin, y_pred_k)
            disp = ConfusionMatrixDisplay(cmatrix, display_labels=[cls, 'Other'])
            disp.plot(cmap=plt.cm.Greens)
            if show:
                plt.show()


