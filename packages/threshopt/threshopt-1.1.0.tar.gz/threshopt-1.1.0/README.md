![Logo](images/logo.png)

[![PyPI version](https://img.shields.io/pypi/v/threshopt?cacheSeconds=1)](https://pypi.org/project/threshopt/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
![GitHub last commit](https://img.shields.io/github/last-commit/salvo-zizzi/threshopt)



**Threshold Optimization Library for Binary and Multiclass Classification**

`threshopt` is a lightweight Python library that automatically finds the optimal decision threshold for classification models.  
Instead of relying on default thresholds (e.g. `0.5`), it optimizes them according to a chosen evaluation metric, improving model performance—especially on imbalanced datasets.

The library is fully compatible with **scikit-learn estimators** and supports both **binary** and **multiclass (fallback-based)** scenarios.

---

## Features

- Automatic optimization of decision thresholds
- Metric-driven optimization (any `sklearn`-style metric or custom metric)
- Cross-validated threshold optimization
- Works with any scikit-learn compatible classifier
- Built-in metrics for imbalanced classification
- Optional visualization utilities
- Multiclass support via one-vs-rest fallback logic

---

## Installation

```bash
pip install threshopt
```

## Quickstart

### Binary classification

```python
from threshopt import optimize_threshold, optimize_threshold_cv, gmean_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import f1_score

# Load data
X, y = load_breast_cancer(return_X_y=True)

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X, y)

# Optimize threshold on the full dataset
best_thresh, best_metric = optimize_threshold(
    model,
    X,
    y,
    metric=f1_score
)

print(f"Best threshold: {best_thresh:.2f}")
print(f"Best F1-score: {best_metric:.4f}")

# Optimize threshold using cross-validation
best_thresh_cv, best_metric_cv = optimize_threshold_cv(
    model,
    X,
    y,
    metric=gmean_score,
    cv=5
)

print(f"CV best threshold: {best_thresh_cv:.2f}")
print(f"CV best G-Mean: {best_metric_cv:.4f}")
```

### Multiclass classification

```python
from threshopt import optimize_threshold, optimize_threshold_cv
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.metrics import f1_score

# Load data
X, y = load_iris(return_X_y=True)

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X, y)

# Optimize thresholds (one per class)
best_thresh, best_metric = optimize_threshold(
    model,
    X,
    y,
    metric=f1_score,
    multiclass=True
)

print("Best thresholds per class:", best_thresh)
print(f"Best F1-score: {best_metric:.4f}")

# Cross-validated multiclass optimization
best_thresh_cv, best_metric_cv = optimize_threshold_cv(
    model,
    X,
    y,
    metric=f1_score,
    cv=5,
    multiclass=True
)

print("CV best thresholds per class:", best_thresh_cv)
print(f"CV best F1-score: {best_metric_cv:.4f}")

```

## Metrics

Included metrics:

-   `gmean_score`: Geometric Mean of sensitivity and specificity
-   `youden_j_stat`: Youden’s J statistic (sensitivity + specificity - 1)
-   `balanced_acc_score`: Balanced Accuracy (wrapper around scikit-learn)

You can also pass any metric function with signature:
```python

 `metric(y_true, y_pred)` -> float 

```
------------------------------------------------------------------------

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

------------------------------------------------------------------------

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
