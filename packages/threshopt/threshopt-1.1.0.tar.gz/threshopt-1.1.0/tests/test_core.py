import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import accuracy_score
from threshopt.core import optimize_threshold

def test_optimize_threshold_binary():
    # Dati sintetici
    X = np.array([[0],[1],[2],[3],[4],[5]])
    y_true = np.array([0,0,1,1,0,1])
    model = LogisticRegression().fit(X, y_true)
    
    thresholds, best_scores = optimize_threshold(
        model, X, y_true, accuracy_score,
        multiclass=False, plot=False, cm=False
    )
    
    assert isinstance(thresholds, float)
    assert isinstance(best_scores, float)
    assert 0 <= thresholds <= 1
    assert best_scores >= 0

def test_optimize_threshold_multiclass():
    # Dati sintetici
    X = np.array([[0,0],[1,0],[0,1],[1,1],[2,0],[0,2]])
    y_true = np.array([0,1,2,1,0,2])
    # LogisticRegression multi-class
    model = OneVsRestClassifier(LogisticRegression()).fit(X, y_true)
    
    thresholds, best_scores = optimize_threshold(
        model, X, y_true, accuracy_score,
        multiclass=True, plot=False, cm=False
    )
    
    assert isinstance(thresholds, np.ndarray)
    assert isinstance(best_scores, np.ndarray)
    assert thresholds.shape[0] == best_scores.shape[0] == len(np.unique(y_true))
    assert np.all((0 <= thresholds) & (thresholds <= 1))
    assert np.all(best_scores >= 0)

