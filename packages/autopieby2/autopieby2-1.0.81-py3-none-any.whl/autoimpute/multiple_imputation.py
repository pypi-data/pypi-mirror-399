"""
Multiple Imputation Module for AutoImpute

Provides a MultipleImputer class that generates N imputed datasets
to capture imputation uncertainty, similar to the MICE approach.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from autoimpute.imputation import AutoImputer

logger = logging.getLogger(__name__)


class MultipleImputer:
    """
    Generator for multiple imputed datasets to capture imputation uncertainty.
    
    This class creates N different imputed versions of a dataset, allowing
    for uncertainty quantification in downstream analysis (e.g., Rubin's rules
    for combining estimates across imputations).
    
    Attributes:
        n_imputations: Number of imputed datasets to generate
        imput_model: Base imputation model to use
        imputer_configs: Configuration for imputation models
        random_state: Base random state for reproducibility
        imputers: List of fitted AutoImputer instances
    """
    
    def __init__(self,
                 n_imputations: int = 5,
                 imput_model: str = 'RandomForest',
                 imputer_configs: Optional[Dict] = None,
                 max_iter: int = 3,
                 random_state: int = 42,
                 n_jobs: int = 1,
                 verbose: bool = True):
        """
        Initialize MultipleImputer.
        
        Parameters:
            n_imputations: Number of imputed datasets to generate (default: 5)
            imput_model: Base ML model for imputation
            imputer_configs: Configuration parameters for models
            max_iter: Number of MICE iterations per imputation
            random_state: Base random seed (each imputation uses random_state + i)
            n_jobs: Number of parallel jobs
            verbose: Print progress messages
        """
        self.n_imputations = n_imputations
        self.imput_model = imput_model
        self.imputer_configs = imputer_configs
        self.max_iter = max_iter
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.verbose = verbose
        self.imputers: List[AutoImputer] = []
        self._is_fitted = False
    
    def fit(self, X: pd.DataFrame) -> 'MultipleImputer':
        """
        Fit multiple imputers on the data.
        
        Parameters:
            X: DataFrame with missing values
            
        Returns:
            self
        """
        self.imputers = []
        
        for i in range(self.n_imputations):
            if self.verbose:
                print(f"Fitting imputer {i + 1}/{self.n_imputations}...")
            
            # Set different random seed for each imputation
            np.random.seed(self.random_state + i)
            
            imputer = AutoImputer(
                imput_model=self.imput_model,
                imputer_configs=self.imputer_configs,
                n_jobs=self.n_jobs,
                max_iter=self.max_iter,
                impute_order='random',  # Randomize order for variability
                verbose=False  # Suppress inner output
            )
            
            imputer.fit_imput(X)
            self.imputers.append(imputer)
        
        self._is_fitted = True
        logger.info(f"Fitted {self.n_imputations} imputers successfully")
        return self
    
    def transform(self, X: pd.DataFrame) -> List[pd.DataFrame]:
        """
        Transform data using all fitted imputers.
        
        Parameters:
            X: DataFrame with missing values
            
        Returns:
            List of N imputed DataFrames
        """
        if not self._is_fitted:
            raise ValueError("MultipleImputer must be fitted before transform")
        
        imputed_datasets = []
        for i, imputer in enumerate(self.imputers):
            if self.verbose:
                print(f"Transforming with imputer {i + 1}/{self.n_imputations}...")
            
            imputed = imputer.transform_imput(X.copy())
            imputed_datasets.append(imputed)
        
        return imputed_datasets
    
    def fit_transform(self, X: pd.DataFrame) -> List[pd.DataFrame]:
        """
        Fit and transform in one step.
        
        Parameters:
            X: DataFrame with missing values
            
        Returns:
            List of N imputed DataFrames
        """
        self.fit(X)
        return self.transform(X)
    
    def get_mean_imputation(self, imputed_datasets: Optional[List[pd.DataFrame]] = None,
                            X: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Get the mean of all imputations for numerical columns.
        
        Parameters:
            imputed_datasets: List of imputed DataFrames (from transform)
            X: Original data (if imputed_datasets not provided)
            
        Returns:
            DataFrame with mean imputed values
        """
        if imputed_datasets is None:
            if X is None:
                raise ValueError("Either imputed_datasets or X must be provided")
            imputed_datasets = self.transform(X)
        
        # Stack and compute mean for numerical columns
        stacked = pd.concat(imputed_datasets, keys=range(len(imputed_datasets)))
        mean_imputed = stacked.groupby(level=1).mean()
        
        # For categorical columns, use mode (most frequent)
        cat_cols = imputed_datasets[0].select_dtypes(include=['object', 'category']).columns
        for col in cat_cols:
            modes = pd.DataFrame([df[col] for df in imputed_datasets]).mode().iloc[0]
            mean_imputed[col] = modes.values
        
        return mean_imputed
    
    def get_imputation_variance(self, imputed_datasets: Optional[List[pd.DataFrame]] = None,
                                 X: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Get variance across imputations for uncertainty estimation.
        
        Parameters:
            imputed_datasets: List of imputed DataFrames
            X: Original data (if imputed_datasets not provided)
            
        Returns:
            DataFrame with variance of imputed values (numerical columns only)
        """
        if imputed_datasets is None:
            if X is None:
                raise ValueError("Either imputed_datasets or X must be provided")
            imputed_datasets = self.transform(X)
        
        # Stack and compute variance
        stacked = pd.concat(imputed_datasets, keys=range(len(imputed_datasets)))
        num_cols = imputed_datasets[0].select_dtypes(include=['int16', 'int32', 'int64', 
                                                               'float16', 'float32', 'float64']).columns
        variance = stacked[num_cols].groupby(level=1).var()
        
        return variance
