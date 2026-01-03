import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Literal
from tqdm import tqdm
from joblib import Parallel, delayed
from atlantic.processing.encoders import AutoLabelEncoder
from atlantic.imputers.imputation import AutoSimpleImputer
from autoimpute.parameters import imputer_parameters                         
from autoimpute.model_selection import imput_models
from autoimpute.models_imputation import RandomForestClassifierImputation, KNNClassifierImputation          

# Configure logging
logger = logging.getLogger(__name__)

parameters = imputer_parameters()

class AutoImputer:
    """
    A supervised machine learning imputation class for handling numerical missing values.
    The class uses a two-step approach:
    1. Initial simple imputation for input features
    2. ML model-based imputation for target columns with missing values
    
    Attributes:
        imput_model (str): Name of the ML model to use for imputation
        imputer_configs (dict): Configuration parameters for the imputation models
        imp_config (dict): Storage for fitted imputers and preprocessors
        numeric_dtypes (set): Set of supported numerical datatypes
        _is_fitted (bool): Flag to track if the imputer has been fitted
    """
    def __init__(self, 
                 imput_model: str,
                 imputer_configs: Dict = parameters,
                 n_jobs: int = 1,
                 max_iter: int = 1,
                 tol: float = 0.001,
                 impute_order: Literal['ascending', 'descending', 'random'] = 'ascending',
                 bounds: Optional[Dict[str, Tuple[float, float]]] = None,
                 enforce_integer: Optional[List[str]] = None,
                 verbose: bool = True):
        """
        Initialize AutoImputer.
        
        Parameters:
            imput_model: Name of the ML model to use ('RandomForest', 'KNN', 'Linear', etc.)
            imputer_configs: Configuration parameters for models
            n_jobs: Number of parallel jobs (-1 uses all cores, 1 is sequential)
            max_iter: Maximum number of imputation iterations (MICE-style). Default is 1 (single pass).
            tol: Tolerance for convergence. Stops early if the sum of absolute differences 
                 in imputed values between iterations is below this threshold.
            impute_order: Order to impute columns - 'ascending' (least missing first), 
                         'descending' (most missing first), or 'random'.
            bounds: Dict mapping column names to (min, max) tuples. Imputed values will be clipped.
            enforce_integer: List of column names that should be rounded to integers after imputation.
            verbose: If True, print progress messages. If False, only log.
        """
        self.imput_model = imput_model
        self.imputer_configs = imputer_configs
        self.n_jobs = n_jobs
        self.max_iter = max_iter
        self.tol = tol
        self.impute_order = impute_order
        self.bounds = bounds or {}
        self.enforce_integer = enforce_integer or []
        self.verbose = verbose
        self.imp_config: Dict[str, Dict] = {}
        self.numeric_dtypes = {'int16', 'int32', 'int64', 'float16', 'float32', 'float64'}
        self._is_fitted = False
        self.encoder = None
        self._iteration_history: List[Dict] = []
        self._feature_importances: Dict[str, Dict[str, float]] = {}  # Track feature importances
        self._encoder_cache: Dict[str, AutoLabelEncoder] = {}  # Cache encoders
    
    def _validate_input(self, X: pd.DataFrame, method: str) -> None:
        """
        Validate input DataFrame.
        
        Args:
            X: Input DataFrame
            method: Method name for error messages ('fit' or 'transform')
            
        Raises:
            ValueError: For invalid inputs
            TypeError: For incorrect data types
        """
        if not isinstance(X, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
            
        if X.empty:
            raise ValueError("Input DataFrame is empty")
            
        if method == 'transform' and not self._is_fitted:
            raise ValueError("MLimputer must be fitted before transform")
            
        # Check for columns with all null values
        null_cols = X.columns[X.isnull().all()].tolist()
        if null_cols:
            raise ValueError(f"Columns {null_cols} contain all null values")
    
    def _get_missing_columns(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Get report of columns with missing values, sorted by impute_order.
        
        Args:
            X: Input DataFrame
            
        Returns:
            DataFrame with missing value statistics
        """
        num_cols = X.select_dtypes(include=self.numeric_dtypes).columns
        missing_stats = pd.DataFrame({
            'null_count': X[num_cols].isna().sum()[X[num_cols].isna().sum() > 0]
        })
        
        if missing_stats.empty:
            return pd.DataFrame()
            
        missing_stats['null_percentage'] = missing_stats['null_count'] / len(X)
        missing_stats['columns'] = missing_stats.index
        
        # Apply impute_order
        if self.impute_order == 'random':
            missing_stats = missing_stats.sample(frac=1).reset_index(drop=True)
        elif self.impute_order == 'descending':
            missing_stats = missing_stats.sort_values('null_percentage', ascending=False).reset_index(drop=True)
        else:  # ascending (default)
            missing_stats = missing_stats.sort_values('null_percentage', ascending=True).reset_index(drop=True)
        
        return missing_stats
    
    def _get_missing_categorical_columns(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Get report of categorical columns with missing values, sorted by impute_order.
        """
        cat_cols = X.select_dtypes(include=['object', 'category']).columns
        missing_stats = pd.DataFrame({
            'null_count': X[cat_cols].isna().sum()[X[cat_cols].isna().sum() > 0]
        })
        
        if missing_stats.empty:
            return pd.DataFrame()
            
        missing_stats['null_percentage'] = missing_stats['null_count'] / len(X)
        missing_stats['columns'] = missing_stats.index
        
        # Apply impute_order
        if self.impute_order == 'random':
            missing_stats = missing_stats.sample(frac=1).reset_index(drop=True)
        elif self.impute_order == 'descending':
            missing_stats = missing_stats.sort_values('null_percentage', ascending=False).reset_index(drop=True)
        else:  # ascending (default)
            missing_stats = missing_stats.sort_values('null_percentage', ascending=True).reset_index(drop=True)
        
        return missing_stats
    
    def _check_convergence(self, prev_imputed: pd.DataFrame, curr_imputed: pd.DataFrame, 
                           columns: list) -> tuple:
        """
        Check if imputation has converged between iterations.
        
        Args:
            prev_imputed: DataFrame from previous iteration
            curr_imputed: DataFrame from current iteration
            columns: List of columns to check for convergence
            
        Returns:
            Tuple of (converged: bool, total_diff: float)
        """
        if prev_imputed is None:
            return False, float('inf')
        
        total_diff = 0.0
        for col in columns:
            if col in prev_imputed.columns and col in curr_imputed.columns:
                # For numeric columns, compute absolute difference
                if prev_imputed[col].dtype in self.numeric_dtypes:
                    diff = (prev_imputed[col] - curr_imputed[col]).abs().sum()
                    total_diff += diff
                else:
                    # For categorical, count number of changes
                    diff = (prev_imputed[col] != curr_imputed[col]).sum()
                    total_diff += diff
        
        return total_diff < self.tol, total_diff
    
    def fit_imput(self, 
                  X:pd.DataFrame):
        """
        
        This method fits missing data in a dataframe using the imputation method specified by the user.
        Supports iterative (MICE-style) imputation when max_iter > 1.
        
        Parameters:
        X (pd.DataFrame): The input pandas dataframe that needs to be imputed.
        
        """
        
        self._validate_input(X, method='fit')
        X_ = X.copy()
        
        missing_report = self._get_missing_columns(X_)
        missing_cat_report = self._get_missing_categorical_columns(X_)
        
        if missing_report.empty and missing_cat_report.empty:
            raise ValueError("No missing values found in any columns")
            
        imp_targets = missing_report['columns'].tolist() if not missing_report.empty else []
        cat_imp_targets = missing_cat_report['columns'].tolist() if not missing_cat_report.empty else []
        all_targets = imp_targets + cat_imp_targets
        
        # Store original missing indices for each column
        self._missing_indices = {}
        for col in all_targets:
            self._missing_indices[col] = X_[X_[col].isnull()].index.tolist()
        
        # Helper function for fitting a single numerical column
        def _fit_numerical_column(target, X_data, imputer_configs, imput_model):
            total_index = X_data.index.tolist()
            test_index = X_data[X_data[target].isnull()].index.tolist()
            train_index = [value for value in total_index if value not in test_index]
            
            train = X_data.iloc[train_index]
            
            cat_cols = [col for col in train.select_dtypes(include=['object', 'category']).columns if col != target]
            
            encoder = None
            if len(cat_cols) > 0:
                encoder = AutoLabelEncoder()
                encoder.fit(X=train[cat_cols])
                train = encoder.transform(X=train)
            
            simple_imputer = AutoSimpleImputer(strategy='mean')
            simple_imputer.fit(train)
            train = simple_imputer.transform(train.copy())
            
            model = imput_models(train=train,
                                 target=target,
                                 parameters=imputer_configs,
                                 algo=imput_model)
            
            return target, {'model': model,
                           'pre_process': encoder,
                           'imputer': simple_imputer,
                           'is_categorical': False}
        
        # Helper function for fitting a single categorical column
        def _fit_categorical_column(target, X_data, imputer_configs, imput_model, encoder_ref):
            total_index = X_data.index.tolist()
            test_index = X_data[X_data[target].isnull()].index.tolist()
            train_index = [value for value in total_index if value not in test_index]
            
            train = X_data.iloc[train_index]
            
            cat_cols = [col for col in train.select_dtypes(include=['object', 'category']).columns if col != target]
            
            target_encoder = AutoLabelEncoder()
            target_encoder.fit(X=train[[target]])
            train = target_encoder.transform(X=train)
            
            cat_encoder = None
            if len(cat_cols) > 0:
                cat_encoder = AutoLabelEncoder()
                cat_encoder.fit(X=train[cat_cols])
                train = cat_encoder.transform(X=train)
            
            simple_imputer = AutoSimpleImputer(strategy='mean')
            simple_imputer.fit(train)
            train = simple_imputer.transform(train.copy())
            
            if imput_model == 'KNN':
                clf_model = KNNClassifierImputation(**imputer_configs.get('KNN', {}))
            else:
                clf_model = RandomForestClassifierImputation(**imputer_configs.get('RandomForest', {}))
            
            sel_cols = [col for col in train.columns if col != target] + [target]
            train = train[sel_cols]
            X_train = train.iloc[:, 0:(len(sel_cols)-1)].values
            y_train = train.iloc[:, (len(sel_cols)-1)].values
            clf_model.fit(X_train, y_train)
            
            return target, {'model': clf_model,
                           'pre_process': cat_encoder,
                           'imputer': simple_imputer,
                           'target_encoder': target_encoder,
                           'is_categorical': True}
        
        # Iterative imputation loop
        prev_imputed = None
        self._iteration_history = []
        
        for iteration in range(self.max_iter):
            self.imp_config = {}  # Reset config each iteration
            
            iter_desc = f"Iteration {iteration + 1}/{self.max_iter}" if self.max_iter > 1 else ""
            
            # Fit numerical columns (parallel or sequential based on n_jobs)
            if self.n_jobs == 1:
                for target in tqdm(imp_targets, desc=f"Fitting Numerical {iter_desc}".strip(), ncols=80):
                    target_name, config = _fit_numerical_column(target, X_, self.imputer_configs, self.imput_model)
                    self.imp_config[target_name] = config
            else:
                results = Parallel(n_jobs=self.n_jobs)(
                    delayed(_fit_numerical_column)(target, X_, self.imputer_configs, self.imput_model)
                    for target in imp_targets
                )
                for target_name, config in results:
                    self.imp_config[target_name] = config
            
            # Fit categorical columns (parallel or sequential based on n_jobs)
            if self.n_jobs == 1:
                for target in tqdm(cat_imp_targets, 
                                   desc = f"Fitting Categorical {iter_desc}".strip(), 
                                   ncols = 80):
                    target_name, config = _fit_categorical_column(target, X_, self.imputer_configs, self.imput_model, self.encoder)
                    self.imp_config[target_name] = config
                    if config['pre_process'] is not None:
                        self.encoder = config['pre_process']
            else:
                # Parallel categorical fitting
                results = Parallel(n_jobs=self.n_jobs)(
                    delayed(_fit_categorical_column)(target, X_, self.imputer_configs, self.imput_model, self.encoder)
                    for target in cat_imp_targets
                )
                for target_name, config in results:
                    self.imp_config[target_name] = config
                    if config['pre_process'] is not None:
                        self.encoder = config['pre_process']
            
            self._is_fitted = True
            
            # Transform to get current imputed values
            curr_imputed = self.transform_imput(X.copy())
            
            # Check convergence
            converged, diff = self._check_convergence(prev_imputed, curr_imputed, all_targets)
            self._iteration_history.append({'iteration': iteration + 1, 'diff': diff})
            
            if self.max_iter > 1:
                msg = f"Iteration {iteration + 1}: Total difference = {diff:.6f}"
                logger.info(msg)
                if self.verbose:
                    print(msg)
            
            if converged and iteration > 0:
                msg = f"Converged after {iteration + 1} iterations (diff={diff:.6f} < tol={self.tol})"
                logger.info(msg)
                if self.verbose:
                    print(msg)
                break
            
            # For next iteration, use imputed data as input
            if iteration < self.max_iter - 1:
                X_ = curr_imputed.copy()
                prev_imputed = curr_imputed.copy()
        
        return self
    
    
    def transform_imput(self,
                        X : pd.DataFrame):
        """
        Imputation of missing values in a X using a pre-fit imputation model.
        
        Parameters:
        -----------
        X: pd.DataFrame
            The X containing missing values to be imputed.
            
        Returns:
        --------
        X_: pd.DataFrame
            The original X with missing values imputed.
        """
        self._validate_input(X, method='transform')
        X_ = X.copy()
        
        for col in tqdm(list(self.imp_config.keys()) , desc = "Imputing Missing Data", ncols = 80):
            
            target = col
            test_index = X_[X_[target].isnull()].index.tolist()
            
            if len(test_index) == 0:
                continue
                
            test = X_.iloc[test_index]
            
            config = self.imp_config[target]
            is_categorical = config.get('is_categorical', False)
            
            encoder = config['pre_process']
            # Transform the DataFrame using Label
            if encoder is not None: 
                test = encoder.transform(X=test)
            
            # For categorical targets, encode the target column too
            if is_categorical:
                target_encoder = config['target_encoder']
                # Don't transform target since it's null - just need to prep features
            
            # Impute the DataFrame using Simple Imputer
            simple_imputer = config['imputer']
            test = simple_imputer.transform(test.copy())  
            
            sel_cols = [c for c in test.columns if c != target] + [target]
            test = test[sel_cols]
            X_test = test.iloc[:, 0:(len(sel_cols)-1)].values
    
            model = config['model']
        
            y_predict = model.predict(X_test)
            
            # For categorical, inverse transform back to original labels
            if is_categorical:
                target_encoder = config['target_encoder']
                # Create a temp df to inverse transform
                temp_df = pd.DataFrame({target: y_predict.astype(int)})
                temp_df = target_encoder.inverse_transform(X=temp_df)
                y_predict = temp_df[target].values
    
            # Apply bounds if specified
            if target in self.bounds and not is_categorical:
                min_val, max_val = self.bounds[target]
                y_predict = np.clip(y_predict, min_val, max_val)
                logger.debug(f"Applied bounds [{min_val}, {max_val}] to column '{target}'")
            
            # Enforce integer if specified
            if target in self.enforce_integer and not is_categorical:
                y_predict = np.round(y_predict).astype(int)
                logger.debug(f"Enforced integer type for column '{target}'")
    
            X_.loc[test_index, target] = y_predict
    
        return X_

    def get_model_info(self) -> Dict[str, Dict]:
        """
        Get information about fitted models and their configurations.
        
        Returns:
            Dictionary containing model configurations and statistics
        """
        if not self._is_fitted:
            raise ValueError("AutoImputer must be fitted first")
            
        return {
            'imputation_model': self.imput_model,
            'imputated_columns': list(self.imp_config.keys()),
            'model_configs': self.imputer_configs[self.imput_model],
            'impute_order': self.impute_order,
            'bounds': self.bounds,
            'enforce_integer': self.enforce_integer
        }
    
    def get_feature_importance(self, column: Optional[str] = None) -> Dict[str, Dict[str, float]]:
        """
        Get feature importance scores for imputation models.
        
        Only available for tree-based models (RandomForest, ExtraTrees, GBR, XGBoost, LightGBM, CatBoost).
        
        Parameters:
            column: Specific column to get importance for. If None, returns all.
            
        Returns:
            Dictionary mapping column names to feature importance dicts.
        """
        if not self._is_fitted:
            raise ValueError("AutoImputer must be fitted first")
        
        importances = {}
        
        columns_to_check = [column] if column else list(self.imp_config.keys())
        
        for col in columns_to_check:
            if col not in self.imp_config:
                continue
                
            config = self.imp_config[col]
            model = config['model']
            
            # Try to get feature importance from the underlying model
            if hasattr(model, 'model') and hasattr(model.model, 'feature_importances_'):
                importance_values = model.model.feature_importances_
                # Get feature names (all columns except target)
                feature_names = [c for c in self.imp_config.keys() if c != col]
                # If mismatch in length, use generic names
                if len(feature_names) != len(importance_values):
                    feature_names = [f"feature_{i}" for i in range(len(importance_values))]
                
                importances[col] = dict(zip(feature_names, importance_values.tolist()))
        
        self._feature_importances = importances
        return importances if column is None else importances.get(column, {})