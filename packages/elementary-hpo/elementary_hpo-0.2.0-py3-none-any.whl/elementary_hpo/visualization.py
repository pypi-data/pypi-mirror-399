import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_optimization_results(results_df: pd.DataFrame):
    """
    Plots the optimization trace.

    Parameters:
    - results_df: DataFrame containing optimization results with 'score' column.
    """
    if results_df.empty:
        print("No results to plot.")
        return

    # Calculate cumulative best score
    results_df = results_df.copy()
    results_df['best_score'] = results_df['score'].cummax()

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    # Plot Optimization Trace
    ax.plot(results_df.index + 1, results_df['best_score'], 
             marker='o', linestyle='-', color='b', alpha=0.6)
    ax.set_title("Optimization Performance (Best Score vs Iteration)")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Best CV Accuracy")
    ax.grid(True, alpha=0.3)
    ax.legend(['Best Score'])

    plt.tight_layout()
    plt.show()

def plot_space_coverage(results_df: pd.DataFrame,
                        x_col: str = 'n_estimators', 
                        y_col: str = 'min_samples_split'):
    """
    Plots and a 2D projection of hyperparameter space coverage.

    Parameters:
    - results_df: DataFrame containing optimization results with hyperparameter and 'batch' columns.
    - x_col: Column name for x-axis hyperparameter.
    - y_col: Column name for y-axis hyperparameter.
    """
    if results_df.empty:
        print("No results to plot.")
        return

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    # Plot Space Coverage
    # Differentiate batches by color
    batches = results_df['batch'].unique()
    colors = sns.color_palette("husl", len(batches))
    
    for batch, color in zip(batches, colors):
        subset = results_df[results_df['batch'] == batch]
        ax.scatter(subset[x_col], subset[y_col], 
                    label=batch, s=60, edgecolor='k', color=color)

    ax.set_title(f"Hyperparameter Space Coverage ({x_col} vs {y_col})")
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()