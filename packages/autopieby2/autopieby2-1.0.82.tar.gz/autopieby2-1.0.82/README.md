# AutoImpute

**AutoImpute - Missing Data Imputation Framework for Machine Learning**

AutoImpute is a comprehensive Python library designed to simplify and automate the process of handling missing data in machine learning datasets. It provides a suite of imputation strategies, from simple statistical methods to advanced predictive modeling, ensuring your data is ready for analysis.

## Features

*   **Diverse Imputation Strategies**: Supports mean, median, mode, constant, and predictive imputation (using models like XGBoost, CatBoost, LightGBM).
*   **Automated Workflow**: Streamlines the imputation process, fitting seamlessly into scikit-learn pipelines.
*   **Evaluation Metrics**: Includes tools to evaluate imputation quality and impact on model performance.
*   **Visualization**: Visualize missing data patterns and imputation results.

## Installation

```bash
pip install autopieby2
```

## Usage

```python
from autoimpute.imputation import AutoImputer
import pandas as pd

# Load your data
data = pd.read_csv("your_data.csv")

# Initialize and fit imputer
imputer = AutoImputer()
imputed_data = imputer.fit_transform(data)

print(imputed_data.head())
```

## License

MIT License
