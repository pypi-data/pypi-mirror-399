import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import sys
from unittest.mock import MagicMock



# Mock atlantic before importing autoimpute
sys.modules['atlantic'] = MagicMock()
sys.modules['atlantic.processing'] = MagicMock()
sys.modules['atlantic.processing.encoders'] = MagicMock()
sys.modules['atlantic.imputers'] = MagicMock()
sys.modules['atlantic.imputers.imputation'] = MagicMock()
sys.modules['joblib'] = MagicMock()

# Mock heavy ML libraries
sys.modules['lightgbm'] = MagicMock()
sys.modules['xgboost'] = MagicMock()
sys.modules['catboost'] = MagicMock()
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.neighbors'] = MagicMock()
sys.modules['sklearn.ensemble'] = MagicMock()
sys.modules['sklearn.linear_model'] = MagicMock()

# Setup the specific mocks needed
MockAutoLabelEncoder = MagicMock()
MockAutoSimpleImputer = MagicMock()

sys.modules['atlantic.processing.encoders'].AutoLabelEncoder = MockAutoLabelEncoder
sys.modules['atlantic.imputers.imputation'].AutoSimpleImputer = MockAutoSimpleImputer

# Mock Base classes for MLimputer to inherit from if they are imported from these libs
# (But autoimpute imports them inside the file usually, let's see)
# models_imputation imports directly.

# We also need to make sure when models_imputation imports them, it gets mocks that are callable (classes)
sys.modules['lightgbm'].train = MagicMock()
sys.modules['xgboost'].XGBRegressor = MagicMock()
sys.modules['catboost'].CatBoostRegressor = MagicMock()
sys.modules['sklearn.neighbors'].KNeighborsRegressor = MagicMock()
sys.modules['sklearn.neighbors'].KNeighborsClassifier = MagicMock()
sys.modules['sklearn.ensemble'].RandomForestRegressor = MagicMock()
sys.modules['sklearn.ensemble'].ExtraTreesRegressor = MagicMock()
sys.modules['sklearn.ensemble'].GradientBoostingRegressor = MagicMock()
sys.modules['sklearn.ensemble'].RandomForestClassifier = MagicMock()


from autoimpute.imputation import AutoImputer
from autoimpute.parameters import imputer_parameters

class TestAutoImputer(unittest.TestCase):
    def setUp(self):
        # Create a simple dummy dataset
        self.data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5, np.nan, 7, 8, 9, 10],
            'B': [10, 9, 8, np.nan, 6, 5, 4, 3, 2, 1],
            'C': ['a', 'b', 'a', 'b', 'a', 'b', 'a', 'b', 'a', 'b']
        })
        self.params = imputer_parameters()

        # Configure Mocks to return an array of correct length (1 missing value per col in this data)
        # KNeighborsRegressor is a Class (Mock). Its return value is the Instance (Mock).
        # We need Instance.predict.return_value to be an array.
        
        mock_knn_instance = sys.modules['sklearn.neighbors'].KNeighborsRegressor.return_value
        mock_knn_instance.predict.return_value = np.array([5.5])

        mock_rf_instance = sys.modules['sklearn.ensemble'].RandomForestRegressor.return_value
        mock_rf_instance.predict.return_value = np.array([5.5])


    def test_initialization(self):
        imputer = AutoImputer(imput_model='RandomForest')
        self.assertEqual(imputer.imput_model, 'RandomForest')
        self.assertFalse(imputer._is_fitted)

    def test_fit_transform_knn(self):
        # Test KNN
        imputer = AutoImputer(imput_model='KNN')
        imputer.fit_imput(self.data)
        self.assertTrue(imputer._is_fitted)
        
        imputed_data = imputer.transform_imput(self.data)
        self.assertEqual(imputed_data.isnull().sum().sum(), 0)
        self.assertEqual(imputed_data.shape, self.data.shape)

    def test_fit_transform_rf(self):
        # Test Random Forest (which uses our new BaseImputation)
        self.params["RandomForest"]["n_estimators"] = 5 # Speed up test
        imputer = AutoImputer(imput_model='RandomForest', imputer_configs=self.params)
        imputer.fit_imput(self.data)
        
        imputed_data = imputer.transform_imput(self.data)
        self.assertEqual(imputed_data.isnull().sum().sum(), 0)

    def test_error_if_not_fitted(self):
        imputer = AutoImputer(imput_model='KNN')
        with self.assertRaises(ValueError):
            imputer.transform_imput(self.data)

if __name__ == '__main__':
    unittest.main()
