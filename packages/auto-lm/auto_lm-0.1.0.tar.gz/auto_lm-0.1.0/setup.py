from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="auto_lm",
    version="0.1.0",
    author="Louati Mahdi",
    author_email="your_email@example.com",
    description="Advanced Automated EDA Library for comprehensive data analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/auto_lm",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "tabulate>=0.8.9",
        "statsmodels>=0.12.0",
        "seaborn>=0.11.0",
    ],
    keywords="eda exploratory-data-analysis data-science statistics machine-learning",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/auto_lm/issues",
        "Source": "https://github.com/yourusername/auto_lm",
    },
)