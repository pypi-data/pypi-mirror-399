import numpy as np
import math
from typing import Dict, List, Any

def map_categorical(n_iter: int, categorical_params: Dict[str, List[Any]]) -> Dict[str, np.ndarray]:
    """
    Distributes categorical choices evenly across iterations.

    Args:
        n_iter: Number of iterations/samples.
        categorical_params: Dictionary with parameter names as keys and list of choices as values.

    Returns:
        Dictionary with parameter names as keys and numpy arrays of choices as values.
    """
    categorical_names = list(categorical_params.keys())
    grid_param = {}
    
    for name in categorical_names:
        choices = categorical_params[name]
        if not choices:
            continue
        n_reps = math.ceil(n_iter / len(choices))
        distributed_list = np.tile(choices, n_reps)[:n_iter]
        np.random.shuffle(distributed_list)
        grid_param[name] = distributed_list
        
    return grid_param

def map_parameters(sample_batch: np.ndarray, params_bound: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Maps samples from the [0, 1] unit cube to actual parameter space.

    Args:
        sample_batch: 2D numpy array of shape (n_samples, n_numerical_params) with values in [0, 1].
        params_bound: Dictionary defining bounds (tuples for numerical, lists for categorical).
    
    Returns:
        List of dictionaries, each representing a parameter configuration.
    """
    from scipy.stats import qmc # Import inside to avoid circular deps if any
    
    params = []
    n_iter = sample_batch.shape[0]

    # Separate numerical and categorical
    numerical_params = {k: v for k, v in params_bound.items() if isinstance(v, tuple)}
    categorical_params = {k: v for k, v in params_bound.items() if isinstance(v, list)}

    numerical_names = list(numerical_params.keys())
    categorical_names = list(categorical_params.keys())

    # Handle Numerical
    n_numerical = len(numerical_names)
    if n_numerical > 0:
        l_bounds = np.array([numerical_params[k][0] for k in numerical_names])
        u_bounds = np.array([numerical_params[k][1] for k in numerical_names])
        
        # Slice batch for numerical params
        numerical_samples = sample_batch[:, :n_numerical]
        scaled_params = qmc.scale(numerical_samples, l_bounds, u_bounds)
    else:
        scaled_params = np.empty((n_iter, 0))

    # Handle Categorical
    categorical_grid = {}
    if categorical_names:
        categorical_grid = map_categorical(n_iter, categorical_params)

    # Combine
    for i in range(n_iter):
        current_params = {}
        # Numerical
        for j, name in enumerate(numerical_names):
            original_type = type(numerical_params[name][0])
            current_params[name] = original_type(scaled_params[i][j])
        
        # Categorical
        for name in categorical_names:
            current_params[name] = categorical_grid[name][i]
            
        params.append(current_params)

    return params