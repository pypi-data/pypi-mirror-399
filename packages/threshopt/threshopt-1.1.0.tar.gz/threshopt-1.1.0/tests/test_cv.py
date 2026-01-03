# tests/test_optimize_threshold_cv.py
import pytest
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.dummy import DummyClassifier
from threshopt.cv import optimize_threshold_cv

def test_basic_functionality():
    # Dati sintetici
    X = np.array([[0], [1], [2], [3], [4], [5]])
    y = np.array([0, 0, 1, 1, 0, 1])

    model = LogisticRegression()
    mean_thresh, mean_metric = optimize_threshold_cv(model, X, y, accuracy_score, cv=2, random_state=42)

    assert isinstance(mean_thresh, float)
    assert isinstance(mean_metric, float)
    assert 0 <= mean_thresh <= 1
    assert 0 <= mean_metric <= 1

def test_dummy_model():
    X = np.random.rand(10, 2)
    y = np.array([0, 1]*5)
    model = DummyClassifier(strategy="most_frequent")
    mean_thresh, mean_metric = optimize_threshold_cv(model, X, y, accuracy_score, cv=2, random_state=42)
    assert isinstance(mean_thresh, float)
    assert isinstance(mean_metric, float)

def test_model_without_proba_or_decision_function():
    class WeirdModel:
        def fit(self, X, y):
            return self
    X = np.array([[0], [1], [2]])
    y = np.array([0, 1, 0])
    model = WeirdModel()
    with pytest.raises(ValueError):
        optimize_threshold_cv(model, X, y, lambda a,b: 1, cv=2)

