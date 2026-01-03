# Elementary HPO

[![PyPI version](https://img.shields.io/pypi/v/elementary-hpo.svg?color=blue)](https://pypi.org/project/elementary-hpo/)
[![Python Versions](https://img.shields.io/pypi/pyversions/elementary-hpo.svg)](https://pypi.org/project/elementary-hpo/)
[![Downloads](https://static.pepy.tech/badge/elementary-hpo)](https://pepy.tech/project/elementary-hpo)
[![Monthly Downloads](https://img.shields.io/pypi/dm/elementary-hpo.svg)](https://pypi.org/project/elementary-hpo/)
[![License](https://img.shields.io/pypi/l/elementary-hpo.svg)](https://github.com/BetikuOluwatobi/elementary-hpo/blob/main/LICENSE)

**Elementary-hpo** is a lightweight hyperparameter optimization library built on **Sobol Sequences** (Quasi-Monte Carlo methods).

It is designed to offer a mathematically superior alternative to Grid Search and Random Search by generating low-discrepancy sequences that cover the hyperparameter search space more evenly and efficiently. Unlike standard Random Search, `elementary-hpo` is **sequential** and **deterministic**, allowing you to pause a search, analyze results, and generate new hyperparameter candidates that mathematically fill the "gaps" of previous runs without redundancy.

Based on concepts discussed in the research paper *[Hyperparameter Optimization in Machine Learning](https://arxiv.org/abs/2410.22854)*, this package optimizes any scikit-learn compatible estimator (e.g., `SVC`, `XGBClassifier`, `GradientBoostingRegressor`).

## 🚀 Key Features
* **Gap-Filling Strategy**: Unlike Random Search, which can cluster points wastefully, Sobol sequences are designed to fill the empty spaces in your search grid progressively.
* **Pause & Resume**: Run a batch of 10 trials, check the results, and run 10 more. The optimizer remembers where it left off and continues exploring new areas of the hyperparameter space.
* **Scikit-Learn Compatible**: Works seamlessly with any estimator that follows the sklearn API.
* **Lightweight**: Minimal dependencies, focused purely on efficient parameter generation.

## Installation

### Using pip
```bash
pip install elementary-hpo

```

### Using Poetry

If you are using Poetry for your project, add it as a dependency:

```bash
poetry add elementary-hpo

```

## Quick Start

### Basic Usage (Random Forest)

Here is a complete example of how to optimize a Random Forest classifier.

```python
from sklearn.datasets import make_classification
from elementary_hpo import SobolOptimizer, plot_optimization_results, plot_space_coverage

# 1. Generate Data
X, y = make_classification(n_samples=1000, n_features=20, random_state=42)

# 2. Define Search Space
# Keys must match the estimator's parameter names
param_bounds = {
    'n_estimators': (50, 300),          # Integer tuple = Numerical range
    'max_depth': (3, 20),
    'min_samples_split': (0.01, 0.5),   # Float tuple = Numerical range
    'criterion': ['gini', 'entropy']    # List = Categorical choices
}

# 3. Initialize Optimizer
optimizer = SobolOptimizer(param_bounds)

# 4. Run Optimization (Phase 1)
# Optimizes a hypothetical estimator logic (or pass your actual model training function here)
optimizer.optimize(X, y, n_samples=8, batch_name="Batch 1")

# 5. Extend Optimization (Phase 2)
# This second run automatically detects the previous points and fills the "gaps"
optimizer.optimize(X, y, n_samples=8, batch_name="Batch 2")

# 6. Analyze Results
print("Best Parameters:", optimizer.get_best_params())

# Visualizations
plot_optimization_results(optimizer.results)
plot_space_coverage(optimizer.results, x_col="n_estimators", y_col="max_depth")

```

## Citation

If you use this package, please consider citing the foundational paper:

> **"Hyperparameter Optimization in Machine Learning"** (2024). arXiv:2410.22854.
> Available at: https://arxiv.org/abs/2410.22854

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License - see the [LICENSE](https://github.com/BetikuOluwatobi/elementary-hpo/blob/main/LICENSE) file for details.