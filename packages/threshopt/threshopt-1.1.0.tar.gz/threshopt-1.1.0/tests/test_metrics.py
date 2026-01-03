import numpy as np
import pytest
from threshopt.metrics import gmean_score, youden_j_stat, balanced_acc_score

def test_gmean_score_basic():
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 1, 1, 1])
    score = gmean_score(y_true, y_pred)
    assert isinstance(score, float)
    assert 0 <= score <= 1

def test_youden_j_stat_basic():
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 1, 1, 1])
    score = youden_j_stat(y_true, y_pred)
    assert isinstance(score, float)
    assert -1 <= score <= 1

def test_balanced_acc_score_basic():
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 1, 1, 1])
    score = balanced_acc_score(y_true, y_pred)
    assert isinstance(score, float)
    assert 0 <= score <= 1

def test_edge_cases():
    # Tutti zero
    y_true = np.array([0,0,0,0])
    y_pred = np.array([0,0,0,0])
    assert gmean_score(y_true, y_pred) == 0
    assert youden_j_stat(y_true, y_pred) == 0
    assert balanced_acc_score(y_true, y_pred) == 1  # sklearn restituisce 1 in questo caso
