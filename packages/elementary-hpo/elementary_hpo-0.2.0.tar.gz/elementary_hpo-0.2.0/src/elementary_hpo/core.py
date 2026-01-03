import numpy as np
import pandas as pd
import math
import warnings
from scipy.stats import qmc
from sklearn.base import is_classifier, is_regressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from typing import Dict, Any, Type, Optional, Tuple
from .utils import map_parameters

class SobolOptimizer:
    def __init__(self, 
                 param_bounds: Dict[str, Any],
                 model_class: Any = RandomForestClassifier,
                 fixed_params: Optional[Dict[str, Any]] = None, 
                 random_state: int = 42):
        """
        Initialize the optimizer with parameter bounds.
        
        Args:
            param_bounds: Dictionary defining bounds (tuples for numerical, lists for categorical).
            model_class: The scikit-learn estimator class to optimize (not an instance).
                         e.g., RandomForestClassifier, SVC, XGBRegressor.
            fixed_params: Dictionary of parameters to pass to the model constructor
                          that are NOT being optimized (e.g., {'n_jobs': -1, 'random_state': 42}).
            random_state: Seed for reproducibility in Sobol sequence.
        """
        self.param_bounds = param_bounds
        self.numerical_keys = [k for k, v in param_bounds.items() if isinstance(v, tuple)]
        self.d = len(self.numerical_keys)
        self.fixed_params = fixed_params or {}
        self.model_class = model_class
        
        # Initialize Sobol Engine
        # Scramble=True allows expanding the sequence later
        self.sampler = qmc.Sobol(d=self.d, scramble=True, seed=random_state)
        
        self.results = pd.DataFrame()
    
    def _check_power_of_two(self, n: int):
        """Warns if n is not a power of 2."""
        if n <= 0: 
            return
        # Check if log2 is an integer
        if not math.log2(n).is_integer():
            warnings.warn(
                f"n_samples ({n}) is not a power of 2. Sobol sequences perform best "
                "when sample counts are powers of 2 (e.g., 8, 16, 32, 64, 128, 256).",
                UserWarning
            )

    def _evaluate_batch(self, 
                        params_list: list, 
                        X: np.ndarray, 
                        y: np.ndarray, 
                        batch_name: str, 
                        metric: str, 
                        cv: int,
                        n_jobs: int) -> pd.DataFrame:
        
        results_data = []
        print(f"--- Processing {batch_name} ({len(params_list)} samples) ---")

        for param in params_list:
            # Merge fixed parameters (e.g., random_state) with current hyperparams
            param.update(self.fixed_params)

            try:
                model = self.model_class(**param)
                # Cross Validation
                # n_jobs controls parallelization of the CV folds
                scores = cross_val_score(model, X, y, cv=cv, scoring=metric, n_jobs=n_jobs)
                mean_score = scores.mean()
            except Exception as e:
                print(f"Error evaluating params {param}: {e}")
                mean_score = float('-inf')  # Assign worst score on failure
            
            # Record results
            entry = param.copy()
            entry['score'] = mean_score
            entry['batch'] = batch_name
            results_data.append(entry)

        return pd.DataFrame(results_data)

    def optimize(self, 
                 X: np.ndarray, 
                 y: np.ndarray, 
                 n_samples: int, 
                 batch_name: str = "Batch",
                 metric: str = 'accuracy',
                 cv: int = 3,
                 n_jobs: int = 1) -> pd.DataFrame:
        """
        Generates 'n_samples' new configurations and evaluates them.

        Args:
            X: Feature matrix for training.
            y: Target vector for training.
            n_samples: Number of new parameter configurations to generate.
            batch_name: Identifier for the batch of evaluations.
            metric: Scikit-learn Scoring metric for evaluation (e.g., 'accuracy', 'neg_mean_squared_error').
            cv: Number of cross-validation folds.
            n_jobs: Number of parallel jobs for cross-validation (-1 uses all cores).
        Returns:
            DataFrame with evaluation results for the new configurations.
        """
        # Sobol works best with powers of 2
        # Guardrail: Check for power of 2
        self._check_power_of_two(n_samples)
        
        # Generate raw samples from unit hypercube
        sample_batch = self.sampler.random(n=n_samples)
        
        # Map to actual dictionary parameters
        params = map_parameters(sample_batch, self.param_bounds)
        
        # Evaluate the batch
        new_results = self._evaluate_batch(params, X, y, batch_name, metric, cv=cv, n_jobs=n_jobs)
        
        # Append to history
        self.results = pd.concat([self.results, new_results], ignore_index=True)
        
        return new_results

    def get_best_params(self) -> Dict[str, Any]:
        """Returns the single best parameter set found so far."""
        if self.results.empty:
            return {}
        
        # Drop rows where scoring failed
        valid_results = self.results.dropna(subset=['score'])
        if valid_results.empty:
            return {}
        
        best_row = valid_results.loc[valid_results['score'].idxmax()]
        # Filter out metadata columns to return clean params
        return {k: v for k, v in best_row.items() if k not in ['score', 'batch']}