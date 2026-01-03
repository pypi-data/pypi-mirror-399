import numpy as np
import pytest
import matplotlib
matplotlib.use('Agg')  # evita di aprire finestre grafiche durante i test
from threshopt.plotting import plot_probability_distribution, plot_confusion_matrix_custom

def test_plot_probability_distribution_binary():
    y_true = np.array([0,0,1,1])
    y_scores = np.array([[0.1,0.9],[0.8,0.2],[0.3,0.7],[0.6,0.4]])
    threshold = 0.5
    # Non deve sollevare errori
    plot_probability_distribution(y_true, y_scores, threshold)

def test_plot_probability_distribution_multiclass():
    y_true = np.array([0,1,2,1,0,2])
    y_scores = np.array([
        [0.7,0.2,0.1],
        [0.1,0.6,0.3],
        [0.2,0.2,0.6],
        [0.1,0.7,0.2],
        [0.8,0.1,0.1],
        [0.2,0.2,0.6]
    ])
    thresholds = [0.5,0.5,0.5]
    plot_probability_distribution(y_true, y_scores, thresholds)

def test_plot_confusion_matrix_custom_binary():
    y_true = np.array([0,0,1,1])
    y_scores = np.array([[0.1,0.9],[0.8,0.2],[0.3,0.7],[0.6,0.4]])
    threshold = 0.5
    plot_confusion_matrix_custom(y_true, y_scores, threshold, report=False, show=False)

def test_plot_confusion_matrix_custom_multiclass():
    y_true = np.array([0,1,2,1,0,2])
    y_scores = np.array([
        [0.7,0.2,0.1],
        [0.1,0.6,0.3],
        [0.2,0.2,0.6],
        [0.1,0.7,0.2],
        [0.8,0.1,0.1],
        [0.2,0.2,0.6]
    ])
    thresholds = [0.5,0.5,0.5]
    plot_confusion_matrix_custom(y_true, y_scores, thresholds, report=False, show=False)
