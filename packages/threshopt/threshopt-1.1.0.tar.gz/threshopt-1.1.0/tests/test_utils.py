import numpy as np
import pytest
from threshopt.utils import sigmoid, softmax, validate_inputs

def test_sigmoid_basic():
    x = np.array([-1, 0, 1])
    s = sigmoid(x)
    assert isinstance(s, np.ndarray)
    assert s.shape == x.shape
    assert np.all((0 <= s) & (s <= 1))

def test_softmax_basic():
    x = np.array([[1,2,3],[0,0,0]])
    s = softmax(x)
    assert isinstance(s, np.ndarray)
    assert s.shape == x.shape
    # Somma delle probabilità per ogni riga = 1
    assert np.allclose(np.sum(s, axis=1), 1)

def test_validate_inputs_basic():
    y_true = [0,1,1]
    y_scores = [[0.1,0.9],[0.8,0.2],[0.3,0.7]]
    y_true_arr, y_scores_arr = validate_inputs(y_true, y_scores)
    assert isinstance(y_true_arr, np.ndarray)
    assert isinstance(y_scores_arr, np.ndarray)
    assert y_true_arr.shape[0] == y_scores_arr.shape[0]

def test_validate_inputs_mismatch():
    y_true = [0,1]
    y_scores = [[0.1,0.9],[0.8,0.2],[0.3,0.7]]
    with pytest.raises(ValueError):
        validate_inputs(y_true, y_scores)
