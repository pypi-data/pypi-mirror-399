from autoimpute.imputation import AutoImputer
from autoimpute.multiple_imputation import MultipleImputer

# Visualization imports are optional (require matplotlib and seaborn)
try:
    from autoimpute.visualization import (
        plot_missingness_heatmap,
        plot_missingness_summary,
        plot_distribution_comparison,
        plot_imputation_convergence
    )
    _VIZ_AVAILABLE = True
except ImportError:
    _VIZ_AVAILABLE = False
    plot_missingness_heatmap = None
    plot_missingness_summary = None
    plot_distribution_comparison = None
    plot_imputation_convergence = None

# For backwards compatibility
MLimputer = AutoImputer

__all__ = [
    'AutoImputer',
    'MLimputer',
    'MultipleImputer',
    'plot_missingness_heatmap',
    'plot_missingness_summary',
    'plot_distribution_comparison',
    'plot_imputation_convergence'
]
