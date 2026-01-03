"""
AutoImpute Visualization Module

Provides tools for visualizing missing data patterns and comparing
distributions before and after imputation.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Union


def plot_missingness_heatmap(df: pd.DataFrame,
                              figsize: tuple = (12, 8),
                              cmap: str = 'YlOrRd',
                              title: str = 'Missing Data Heatmap',
                              ax: Optional[plt.Axes] = None) -> plt.Axes:
    """
    Create a heatmap visualization of missing values in a DataFrame.
    
    Each cell represents a value in the DataFrame:
    - Light color = present
    - Dark color = missing
    
    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame to visualize.
    figsize : tuple, optional
        Figure size as (width, height). Default is (12, 8).
    cmap : str, optional
        Colormap to use. Default is 'YlOrRd'.
    title : str, optional
        Title for the plot.
    ax : plt.Axes, optional
        Existing axes to plot on. If None, creates new figure.
        
    Returns:
    --------
    plt.Axes
        The matplotlib Axes object containing the plot.
        
    Example:
    --------
    >>> import pandas as pd
    >>> from autoimpute.visualization import plot_missingness_heatmap
    >>> df = pd.DataFrame({'A': [1, np.nan, 3], 'B': [np.nan, 2, 3]})
    >>> ax = plot_missingness_heatmap(df)
    >>> plt.show()
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    # Create a boolean mask (True = missing)
    missing_mask = df.isnull().astype(int)
    
    # Plot heatmap
    sns.heatmap(missing_mask, 
                cmap=cmap, 
                cbar_kws={'label': 'Missing (1) / Present (0)'},
                yticklabels=False,  # Hide row labels for large datasets
                ax=ax)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Columns', fontsize=12)
    ax.set_ylabel('Rows', fontsize=12)
    
    # Rotate column labels for better readability
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    return ax


def plot_missingness_summary(df: pd.DataFrame,
                              figsize: tuple = (10, 6),
                              color: str = '#e74c3c',
                              title: str = 'Missing Values by Column',
                              ax: Optional[plt.Axes] = None) -> plt.Axes:
    """
    Create a bar chart showing the percentage of missing values per column.
    
    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame to analyze.
    figsize : tuple, optional
        Figure size as (width, height). Default is (10, 6).
    color : str, optional
        Bar color. Default is '#e74c3c'.
    title : str, optional
        Title for the plot.
    ax : plt.Axes, optional
        Existing axes to plot on.
        
    Returns:
    --------
    plt.Axes
        The matplotlib Axes object containing the plot.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate missing percentages
    missing_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
    missing_pct = missing_pct[missing_pct > 0]  # Only show columns with missing values
    
    if missing_pct.empty:
        ax.text(0.5, 0.5, 'No missing values found!', 
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.set_title(title)
        return ax
    
    # Create bar plot
    bars = ax.bar(range(len(missing_pct)), missing_pct.values, color=color, edgecolor='black')
    
    ax.set_xticks(range(len(missing_pct)))
    ax.set_xticklabels(missing_pct.index, rotation=45, ha='right')
    ax.set_ylabel('Missing (%)', fontsize=12)
    ax.set_xlabel('Column', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Add percentage labels on bars
    for bar, pct in zip(bars, missing_pct.values):
        ax.annotate(f'{pct:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords='offset points',
                    ha='center', va='bottom', fontsize=9)
    
    ax.set_ylim(0, max(missing_pct.values) * 1.15)  # Add headroom for labels
    plt.tight_layout()
    return ax


def plot_distribution_comparison(original: pd.DataFrame,
                                  imputed: pd.DataFrame,
                                  column: str,
                                  figsize: tuple = (10, 5),
                                  color_original: str = '#3498db',
                                  color_imputed: str = '#e74c3c',
                                  title: Optional[str] = None,
                                  ax: Optional[plt.Axes] = None) -> plt.Axes:
    """
    Compare the distribution of a column before and after imputation.
    
    For numerical columns, overlays KDE plots.
    For categorical columns, shows side-by-side bar plots.
    
    Parameters:
    -----------
    original : pd.DataFrame
        The original DataFrame (with missing values).
    imputed : pd.DataFrame
        The imputed DataFrame (without missing values).
    column : str
        The column name to compare.
    figsize : tuple, optional
        Figure size. Default is (10, 5).
    color_original : str, optional
        Color for original distribution.
    color_imputed : str, optional
        Color for imputed distribution.
    title : str, optional
        Custom title. If None, generates one automatically.
    ax : plt.Axes, optional
        Existing axes to plot on.
        
    Returns:
    --------
    plt.Axes
        The matplotlib Axes object containing the plot.
        
    Example:
    --------
    >>> from autoimpute.visualization import plot_distribution_comparison
    >>> ax = plot_distribution_comparison(df_original, df_imputed, 'Age')
    >>> plt.show()
    """
    if column not in original.columns or column not in imputed.columns:
        raise ValueError(f"Column '{column}' not found in one or both DataFrames")
    
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    orig_col = original[column].dropna()
    imp_col = imputed[column]
    
    # Determine if numerical or categorical
    is_numeric = pd.api.types.is_numeric_dtype(imp_col)
    
    if is_numeric:
        # KDE plot for numerical data
        if len(orig_col) > 1:
            sns.kdeplot(orig_col, ax=ax, color=color_original, 
                       label=f'Original (n={len(orig_col)})', linewidth=2, fill=True, alpha=0.3)
        if len(imp_col) > 1:
            sns.kdeplot(imp_col, ax=ax, color=color_imputed, 
                       label=f'Imputed (n={len(imp_col)})', linewidth=2, fill=True, alpha=0.3)
        
        ax.set_xlabel(column, fontsize=12)
        ax.set_ylabel('Density', fontsize=12)
    else:
        # Bar plot for categorical data
        orig_counts = orig_col.value_counts(normalize=True).sort_index()
        imp_counts = imp_col.value_counts(normalize=True).sort_index()
        
        # Align categories
        all_cats = sorted(set(orig_counts.index) | set(imp_counts.index))
        x = np.arange(len(all_cats))
        width = 0.35
        
        orig_vals = [orig_counts.get(cat, 0) for cat in all_cats]
        imp_vals = [imp_counts.get(cat, 0) for cat in all_cats]
        
        ax.bar(x - width/2, orig_vals, width, label='Original', color=color_original, edgecolor='black')
        ax.bar(x + width/2, imp_vals, width, label='Imputed', color=color_imputed, edgecolor='black')
        
        ax.set_xticks(x)
        ax.set_xticklabels(all_cats, rotation=45, ha='right')
        ax.set_xlabel(column, fontsize=12)
        ax.set_ylabel('Proportion', fontsize=12)
    
    if title is None:
        title = f'Distribution Comparison: {column}'
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend()
    
    plt.tight_layout()
    return ax


def plot_imputation_convergence(iteration_history: List[dict],
                                 figsize: tuple = (8, 5),
                                 color: str = '#2ecc71',
                                 title: str = 'Imputation Convergence',
                                 ax: Optional[plt.Axes] = None) -> plt.Axes:
    """
    Plot the convergence of iterative imputation over iterations.
    
    Parameters:
    -----------
    iteration_history : List[dict]
        List of dicts with 'iteration' and 'diff' keys (from AutoImputer._iteration_history).
    figsize : tuple, optional
        Figure size.
    color : str, optional
        Line color.
    title : str, optional
        Plot title.
    ax : plt.Axes, optional
        Existing axes.
        
    Returns:
    --------
    plt.Axes
        The matplotlib Axes object containing the plot.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    if not iteration_history:
        ax.text(0.5, 0.5, 'No iteration history available', 
                ha='center', va='center', transform=ax.transAxes)
        return ax
    
    iterations = [h['iteration'] for h in iteration_history]
    diffs = [h['diff'] for h in iteration_history]
    
    ax.plot(iterations, diffs, marker='o', color=color, linewidth=2, markersize=8)
    ax.set_xlabel('Iteration', fontsize=12)
    ax.set_ylabel('Total Difference', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(iterations)
    
    # Add grid for readability
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return ax
