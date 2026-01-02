"""Utility functions for auto_lm"""

__version__ = '0.1.0'

import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

def detect_outliers(data):
    """Detect outliers using IQR method"""
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = ((data < lower_bound) | (data > upper_bound)).sum()
    return outliers

def cramers_v(x, y):
    """Calculate Cramér's V for categorical association"""
    confusion_matrix = pd.crosstab(x, y)
    chi2 = stats.chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    return np.sqrt(phi2 / min(k-1, r-1))

def calculate_vif(df):
    """Calculate Variance Inflation Factor"""
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return {}
    
    vif = {}
    for i in range(numeric_df.shape[1]):
        try:
            vif[numeric_df.columns[i]] = variance_inflation_factor(numeric_df.values, i)
        except:
            vif[numeric_df.columns[i]] = 'N/A'
    return vif

def normality_test(data):
    """Perform Shapiro-Wilk test for normality"""
    if len(data) < 3:
        return 'N/A', 'N/A'
    try:
        stat, p_value = stats.shapiro(data[:5000])  # Limit to 5000 samples
        return round(stat, 4), round(p_value, 4)
    except:
        return 'N/A', 'N/A'