import setuptools
from pathlib import Path

this_directory = Path(__file__).parent

# Read README
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements (with fallback for wheel builds)
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    install_requires = requirements_file.read_text().strip().split("\n")
else:
    # Fallback for wheel builds from sdist
    install_requires = [
        "atlantic>=1.1.80",
        "catboost>=1.1.1",
        "xgboost>=1.7.3",
        "lightgbm>=3.3.5",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
    ]

setuptools.setup(
    name="autopieby2",
    version="1.0.82",
    description="AutoImpute - Missing Data Imputation Framework for Machine Learning",
    long_description=long_description,      
    long_description_content_type="text/markdown",
    url="https://github.com/pieby2/AutoImpute",
    author="Prakhar",
    author_email="Prakharpragyan1000@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Customer Service",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Telecommunications Industry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},  
    keywords=[
        "data science",
        "machine learning",
        "data preprocessing",
        "null imputation",
        "predictive null imputation",
        "multiple null imputation",
        "automated machine learning",
    ],           
    install_requires=install_requires,
    python_requires=">=3.8",
)
