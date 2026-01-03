import numpy as np
import pytest
from sklearn.metrics import accuracy_score
from threshopt.thresholds.binary_threshold import best_threshold_binary
from threshopt.thresholds.multiclass_threshold import best_threshold_multiclass

def test_best_threshold_binary_basic():
    y_true = np.array([0, 0, 1, 1])
    y_prob = np.array([0.1, 0.4, 0.6, 0.9])
    
    best_t, best_s = best_threshold_binary(y_true, y_prob, accuracy_score)
    assert isinstance(best_t, float)
    assert 0 <= best_t <= 1
    assert isinstance(best_s, float)
    assert best_s >= 0

def test_best_threshold_multiclass_basic():
    y_true = np.array([0,1,2,1,0,2])
    y_scores = np.array([
        [0.7,0.2,0.1],
        [0.1,0.6,0.3],
        [0.2,0.2,0.6],
        [0.1,0.7,0.2],
        [0.8,0.1,0.1],
        [0.2,0.2,0.6]
    ])
    
    thresholds, best_scores = best_threshold_multiclass(y_true, y_scores, accuracy_score)
    assert thresholds.shape[0] == y_scores.shape[1]
    assert best_scores.shape[0] == y_scores.shape[1]
    assert np.all((0 <= thresholds) & (thresholds <= 1))
    assert np.all(best_scores >= 0)
