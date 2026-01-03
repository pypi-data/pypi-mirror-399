import lightgbm as lgb
import xgboost as xgb
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import Ridge
from catboost import CatBoostRegressor, CatBoostClassifier

class BaseImputation:
    """
    Base class for all imputation models, providing common functionality for 
    fitting, predicting, and parameter handling.
    """
    def fit(self, X, y):
        """
        Fit the underlying model to the provided training data.
        
        Parameters:
            X (array-like): Feature dataset for training.
            y (array-like): Target values.
        """
        if hasattr(self, 'params') and self.__class__.__name__ == 'LightGBMImputation':
             train_data = lgb.Dataset(X, label=y)
             self.model = lgb.train(self.params, train_data, num_boost_round=self.n_estimators)
        else:
            self.model.fit(X, y)
        self.is_fitted_ = True

    def predict(self, X):
        """
        Predict using the fitted model.
        
        Parameters:
            X (array-like): Dataset for which to make predictions.
            
        Returns:
            array: Predicted values.
        """
        self.check_is_fitted()
        return self.model.predict(X)

    def check_is_fitted(self):
        """
        Verify that the model has been fitted.
        """
        if not hasattr(self, 'is_fitted_') or not self.is_fitted_:
             raise AttributeError(f"{self.__class__.__name__} is not fitted yet.")

    def set_params(self, **parameters):
        """
        Set the parameters of this estimator.
        """
        for parameter, value in parameters.items():
            setattr(self, parameter, value)
            if hasattr(self, 'params'): # Update params dict for LightGBM
                self.params[parameter] = value
        self.is_fitted_ = False
        return self


class RandomForestImputation(BaseImputation):
    """
    Random Forest regression model tailored for imputation tasks.
    """
    def __init__(self, n_estimators=100, random_state=42, criterion="squared_error", max_depth=None,
                 min_samples_split=2, min_samples_leaf=1, max_features='sqrt'):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.model = RandomForestRegressor(n_estimators=self.n_estimators, random_state=self.random_state, 
                                           criterion=self.criterion, max_depth=self.max_depth, 
                                           min_samples_split=self.min_samples_split, 
                                           min_samples_leaf=self.min_samples_leaf, max_features=self.max_features)

    def get_params(self, deep=True):
        return {"n_estimators": self.n_estimators, "random_state": self.random_state, "criterion": self.criterion,
                "max_depth": self.max_depth, "min_samples_split": self.min_samples_split, 
                "min_samples_leaf": self.min_samples_leaf, "max_features": self.max_features}


class ExtraTreesImputation(BaseImputation):
    """
    Extra Trees regression model optimized for imputation tasks.
    """
    def __init__(self, n_estimators=100, random_state=42, criterion="squared_error", max_depth=None,
                 min_samples_split=2, min_samples_leaf=1, max_features='sqrt'):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.model = ExtraTreesRegressor(n_estimators=self.n_estimators, random_state=self.random_state, 
                                         criterion=self.criterion, max_depth=self.max_depth, 
                                         min_samples_split=self.min_samples_split, 
                                         min_samples_leaf=self.min_samples_leaf, max_features=self.max_features)

    def get_params(self, deep=True):
        return {"n_estimators": self.n_estimators, "random_state": self.random_state, "criterion": self.criterion,
                "max_depth": self.max_depth, "min_samples_split": self.min_samples_split, 
                "min_samples_leaf": self.min_samples_leaf, "max_features": self.max_features}


class GBRImputation(BaseImputation):
    """
    Gradient Boosting regression model designed for imputation.
    """
    def __init__(self, n_estimators=100, criterion="friedman_mse", learning_rate=0.1, max_depth=3,
                 min_samples_split=2, min_samples_leaf=1, loss='squared_error'):
        self.n_estimators = n_estimators
        self.criterion = criterion
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.loss = loss
        self.model = GradientBoostingRegressor(n_estimators=self.n_estimators, criterion=self.criterion, 
                                               learning_rate=self.learning_rate, max_depth=self.max_depth, 
                                               min_samples_split=self.min_samples_split,
                                               min_samples_leaf=self.min_samples_leaf, loss=self.loss)

    def get_params(self, deep=True):
        return {"n_estimators": self.n_estimators, "criterion": self.criterion, "learning_rate": self.learning_rate,
                "max_depth": self.max_depth, "min_samples_split": self.min_samples_split,
                "min_samples_leaf": self.min_samples_leaf , 'loss': self.loss}


class KNNImputation(BaseImputation):
    """
    K-Nearest Neighbors regressor for imputation tasks.
    """
    def __init__(self, n_neighbors=5, weights='uniform', algorithm='auto', leaf_size=30, p=2):
        self.n_neighbors = n_neighbors
        self.weights = weights
        self.algorithm = algorithm
        self.leaf_size = leaf_size
        self.p = p
        self.model = KNeighborsRegressor(n_neighbors=self.n_neighbors, weights=self.weights, 
                                         algorithm=self.algorithm, leaf_size=self.leaf_size, p=self.p)

    def get_params(self, deep=True):
        return {"n_neighbors": self.n_neighbors, "weights": self.weights, 
                "algorithm": self.algorithm, "leaf_size": self.leaf_size, "p": self.p}


class XGBoostImputation(BaseImputation):
    """
    XGBoost regression model tailored for imputation.
    """
    def __init__(self, n_estimators=100, objective='reg:squarederror', learning_rate=0.1, max_depth=3, 
                 reg_lambda=1, reg_alpha=0, subsample=1, colsample_bytree=1):
        self.n_estimators = n_estimators
        self.objective = objective
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.reg_lambda = reg_lambda
        self.reg_alpha = reg_alpha
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.model = xgb.XGBRegressor(n_estimators=self.n_estimators, learning_rate=self.learning_rate,
                                      max_depth=self.max_depth, reg_lambda=self.reg_lambda, reg_alpha=self.reg_alpha,
                                      subsample=self.subsample, colsample_bytree=self.colsample_bytree, verbosity=0)

    def get_params(self, deep=True):
        return {
            "n_estimators": self.n_estimators, "objective": self.objective, "learning_rate": self.learning_rate, "max_depth": self.max_depth,
            "reg_lambda": self.reg_lambda, "reg_alpha": self.reg_alpha, "subsample": self.subsample, 
            "colsample_bytree": self.colsample_bytree
        }


class CatBoostImputation(BaseImputation):
    """
    CatBoost regression model ideal for imputation.
    """
    def __init__(self, iterations=100, loss_function='RMSE', depth=8, learning_rate=0.1, l2_leaf_reg=3, 
                 border_count=254, subsample=1):
        self.iterations = iterations
        self.loss_function = loss_function
        self.depth = depth
        self.learning_rate = learning_rate
        self.l2_leaf_reg = l2_leaf_reg
        self.border_count = border_count
        self.subsample = subsample
        self.model = CatBoostRegressor(
            iterations=self.iterations,
            loss_function=self.loss_function,
            depth=self.depth,
            learning_rate=self.learning_rate,
            l2_leaf_reg=self.l2_leaf_reg,
            border_count=self.border_count,
            subsample=self.subsample,
            save_snapshot=False,
            verbose=False
        )

    def get_params(self, deep=True):
        return {
            "iterations": self.iterations, "depth": self.depth, "learning_rate": self.learning_rate,
            "l2_leaf_reg": self.l2_leaf_reg, "border_count": self.border_count, "subsample": self.subsample
        }


class LightGBMImputation(BaseImputation):
    """
    LightGBM regression model suited for large datasets.
    """
    def __init__(self, boosting_type='gbdt', objective='regression', metric='mse', num_leaves=31, max_depth=-1, learning_rate=0.1, 
                 n_estimators=100, feature_fraction=0.9, bagging_fraction=0.8, bagging_freq=5, reg_alpha=0.1, 
                 reg_lambda=0.1, verbose=0, force_col_wise=True, min_data_in_leaf=20):
        self.boosting_type = boosting_type
        self.objective = objective
        self.metric = metric
        self.num_leaves = num_leaves
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.n_estimators = n_estimators
        self.feature_fraction = feature_fraction
        self.bagging_fraction = bagging_fraction
        self.bagging_freq = bagging_freq
        self.reg_alpha = reg_alpha
        self.reg_lambda = reg_lambda
        self.verbose = verbose
        self.force_col_wise = force_col_wise
        self.min_data_in_leaf = min_data_in_leaf
        self.params = {
            "boosting_type": self.boosting_type, "objective": self.objective, 'metric': self.metric, "num_leaves": self.num_leaves,
            "max_depth": self.max_depth, "learning_rate": self.learning_rate, "n_estimators": self.n_estimators,
            "feature_fraction": self.feature_fraction, "bagging_fraction": self.bagging_fraction,
            "bagging_freq": self.bagging_freq, "reg_alpha": self.reg_alpha, "reg_lambda": self.reg_lambda,
            "verbose": self.verbose, "force_col_wise": self.force_col_wise, "min_data_in_leaf": self.min_data_in_leaf}

    def get_params(self, deep=True):
        return self.params


class LinearImputation(BaseImputation):
    """
    Ridge (L2-regularized Linear Regression) model for imputation.
    Fast and effective for linear relationships.
    """
    def __init__(self, alpha=1.0, fit_intercept=True, solver='auto', random_state=42):
        self.alpha = alpha
        self.fit_intercept = fit_intercept
        self.solver = solver
        self.random_state = random_state
        self.model = Ridge(alpha=self.alpha, fit_intercept=self.fit_intercept, 
                           solver=self.solver, random_state=self.random_state)

    def get_params(self, deep=True):
        return {"alpha": self.alpha, "fit_intercept": self.fit_intercept, 
                "solver": self.solver, "random_state": self.random_state}


# ============== CLASSIFIER-BASED IMPUTERS (for Categorical data) ==============

class RandomForestClassifierImputation(BaseImputation):
    """
    Random Forest Classifier for imputing categorical (object/category) columns.
    """
    def __init__(self, n_estimators=100, random_state=42, criterion="gini", max_depth=None,
                 min_samples_split=2, min_samples_leaf=1, max_features='sqrt'):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.model = RandomForestClassifier(n_estimators=self.n_estimators, random_state=self.random_state, 
                                            criterion=self.criterion, max_depth=self.max_depth, 
                                            min_samples_split=self.min_samples_split, 
                                            min_samples_leaf=self.min_samples_leaf, max_features=self.max_features)

    def get_params(self, deep=True):
        return {"n_estimators": self.n_estimators, "random_state": self.random_state, "criterion": self.criterion,
                "max_depth": self.max_depth, "min_samples_split": self.min_samples_split, 
                "min_samples_leaf": self.min_samples_leaf, "max_features": self.max_features}


class KNNClassifierImputation(BaseImputation):
    """
    K-Nearest Neighbors Classifier for imputing categorical columns.
    """
    def __init__(self, n_neighbors=5, weights='uniform', algorithm='auto', leaf_size=30, p=2):
        self.n_neighbors = n_neighbors
        self.weights = weights
        self.algorithm = algorithm
        self.leaf_size = leaf_size
        self.p = p
        self.model = KNeighborsClassifier(n_neighbors=self.n_neighbors, weights=self.weights, 
                                          algorithm=self.algorithm, leaf_size=self.leaf_size, p=self.p)

    def get_params(self, deep=True):
        return {"n_neighbors": self.n_neighbors, "weights": self.weights, 
                "algorithm": self.algorithm, "leaf_size": self.leaf_size, "p": self.p}
