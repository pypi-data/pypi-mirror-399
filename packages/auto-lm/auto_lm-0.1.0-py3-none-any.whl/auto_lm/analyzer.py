"""
Main analyzer module for auto_lm
Author: Louati Mahdi
"""

import pandas as pd
import numpy as np
from scipy import stats
from tabulate import tabulate
import warnings
from typing import Optional, Dict, Any, List
import seaborn as sns
from .utils import detect_outliers, cramers_v, calculate_vif, normality_test

warnings.filterwarnings('ignore')

class AutoLM:
    """
    Advanced Automated EDA Library
    Performs comprehensive exploratory data analysis on any DataFrame
    """
    
    def __init__(self, df: pd.DataFrame, target: Optional[str] = None):
        """
        Initialize AutoLM analyzer
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe for analysis
        target : str, optional
            Target variable for supervised analysis
        """
        self.df = df.copy()
        self.target = target
        self.results = {}
        
    def analyze(self, show_plots: bool = False) -> Dict[str, Any]:
        """
        Perform complete EDA analysis
        
        Parameters:
        -----------
        show_plots : bool
            Whether to display plots (set False for table-only output)
        
        Returns:
        --------
        Dict containing all analysis results
        """
        print("\n" + "="*80)
        print(" "*25 + "AUTO_LM - ADVANCED EDA ANALYSIS")
        print("="*80 + "\n")
        
        # Dataset Overview
        self._dataset_overview()
        
        # Univariate Analysis
        self._univariate_analysis()
        
        # Multivariate Analysis
        self._multivariate_analysis()
        
        # Correlation Analysis
        self._correlation_analysis()
        
        # Causation Analysis
        self._causation_analysis()
        
        # Statistical Tests
        self._statistical_tests()
        
        # Display comprehensive table
        self._display_results_table()
        
        return self.results
    
    def _dataset_overview(self):
        """Analyze dataset overview"""
        overview = {
            'Total Rows': len(self.df),
            'Total Columns': len(self.df.columns),
            'Numeric Features': len(self.df.select_dtypes(include=[np.number]).columns),
            'Categorical Features': len(self.df.select_dtypes(include=['object']).columns),
            'Memory Usage (MB)': round(self.df.memory_usage(deep=True).sum() / 1024**2, 2),
            'Missing Values': self.df.isnull().sum().sum(),
            'Missing Percentage': round((self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100, 2),
            'Duplicate Rows': self.df.duplicated().sum()
        }
        self.results['overview'] = overview
    
    def _univariate_analysis(self):
        """Perform univariate analysis for each column"""
        univariate = {}
        
        for col in self.df.columns:
            col_data = self.df[col].dropna()
            col_info = {
                'dtype': str(self.df[col].dtype),
                'missing': self.df[col].isnull().sum(),
                'missing_pct': round((self.df[col].isnull().sum() / len(self.df)) * 100, 2),
                'unique': self.df[col].nunique(),
                'unique_pct': round((self.df[col].nunique() / len(self.df)) * 100, 2)
            }
            
            if pd.api.types.is_numeric_dtype(self.df[col]):
                col_info.update({
                    'mean': round(col_data.mean(), 4),
                    'median': round(col_data.median(), 4),
                    'std': round(col_data.std(), 4),
                    'min': round(col_data.min(), 4),
                    'max': round(col_data.max(), 4),
                    'q25': round(col_data.quantile(0.25), 4),
                    'q75': round(col_data.quantile(0.75), 4),
                    'skewness': round(col_data.skew(), 4),
                    'kurtosis': round(col_data.kurtosis(), 4),
                    'outliers': detect_outliers(col_data),
                    'cv': round((col_data.std() / col_data.mean()) * 100, 2) if col_data.mean() != 0 else 'N/A'
                })
                
                # Normality test
                stat, p_val = normality_test(col_data)
                col_info['normality_stat'] = stat
                col_info['normality_p'] = p_val
                
            else:
                # Categorical analysis
                mode_val = col_data.mode()[0] if not col_data.mode().empty else 'N/A'
                col_info.update({
                    'mode': mode_val,
                    'mode_freq': (col_data == mode_val).sum() if mode_val != 'N/A' else 0,
                    'entropy': round(stats.entropy(col_data.value_counts()), 4)
                })
            
            univariate[col] = col_info
        
        self.results['univariate'] = univariate
    
    def _multivariate_analysis(self):
        """Perform multivariate analysis"""
        multivariate = {}
        
        # Numerical columns correlation matrix
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = self.df[numeric_cols].corr()
            
            # Find strong correlations
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        strong_corr.append({
                            'var1': corr_matrix.columns[i],
                            'var2': corr_matrix.columns[j],
                            'correlation': round(corr_val, 4)
                        })
            
            multivariate['strong_correlations'] = strong_corr
            multivariate['avg_correlation'] = round(corr_matrix.abs().mean().mean(), 4)
            
            # VIF for multicollinearity
            vif_scores = calculate_vif(self.df)
            multivariate['vif_scores'] = vif_scores
        
        # Categorical associations
        cat_cols = self.df.select_dtypes(include=['object']).columns
        if len(cat_cols) > 1:
            cat_associations = []
            for i in range(len(cat_cols)):
                for j in range(i+1, len(cat_cols)):
                    try:
                        cv = cramers_v(self.df[cat_cols[i]], self.df[cat_cols[j]])
                        if cv > 0.3:
                            cat_associations.append({
                                'var1': cat_cols[i],
                                'var2': cat_cols[j],
                                'cramers_v': round(cv, 4)
                            })
                    except:
                        pass
            
            multivariate['categorical_associations'] = cat_associations
        
        self.results['multivariate'] = multivariate
    
    def _correlation_analysis(self):
        """Perform detailed correlation analysis"""
        correlation = {}
        
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] > 1:
            # Pearson correlation
            pearson_corr = numeric_df.corr(method='pearson')
            
            # Spearman correlation
            spearman_corr = numeric_df.corr(method='spearman')
            
            # Kendall correlation
            if numeric_df.shape[1] <= 10:  # Limit for computational efficiency
                kendall_corr = numeric_df.corr(method='kendall')
            else:
                kendall_corr = None
            
            correlation['pearson_avg'] = round(pearson_corr.abs().mean().mean(), 4)
            correlation['spearman_avg'] = round(spearman_corr.abs().mean().mean(), 4)
            if kendall_corr is not None:
                correlation['kendall_avg'] = round(kendall_corr.abs().mean().mean(), 4)
            
            # Target correlations if specified
            if self.target and self.target in numeric_df.columns:
                target_corr = {}
                for col in numeric_df.columns:
                    if col != self.target:
                        target_corr[col] = {
                            'pearson': round(pearson_corr.loc[self.target, col], 4),
                            'spearman': round(spearman_corr.loc[self.target, col], 4)
                        }
                correlation['target_correlations'] = target_corr
        
        self.results['correlation'] = correlation
    
    def _causation_analysis(self):
        """Perform causation analysis using statistical tests"""
        causation = {}
        
        if self.target:
            target_data = self.df[self.target].dropna()
            
            # For numeric target
            if pd.api.types.is_numeric_dtype(target_data):
                causation['target_type'] = 'numeric'
                
                # ANOVA for categorical predictors
                cat_cols = self.df.select_dtypes(include=['object']).columns
                anova_results = {}
                for col in cat_cols:
                    if col != self.target:
                        try:
                            groups = [group.dropna() for name, group in self.df.groupby(col)[self.target]]
                            if len(groups) > 1:
                                f_stat, p_val = stats.f_oneway(*groups)
                                anova_results[col] = {
                                    'f_statistic': round(f_stat, 4),
                                    'p_value': round(p_val, 4),
                                    'significant': p_val < 0.05
                                }
                        except:
                            pass
                
                causation['anova_tests'] = anova_results
                
            # For categorical target
            else:
                causation['target_type'] = 'categorical'
                
                # Chi-square tests
                chi_square_results = {}
                for col in self.df.columns:
                    if col != self.target:
                        try:
                            if pd.api.types.is_categorical_dtype(self.df[col]) or self.df[col].dtype == 'object':
                                chi2, p_val, dof, expected = stats.chi2_contingency(
                                    pd.crosstab(self.df[col], self.df[self.target])
                                )
                                chi_square_results[col] = {
                                    'chi2': round(chi2, 4),
                                    'p_value': round(p_val, 4),
                                    'significant': p_val < 0.05
                                }
                        except:
                            pass
                
                causation['chi_square_tests'] = chi_square_results
        
        self.results['causation'] = causation
    
    def _statistical_tests(self):
        """Perform additional statistical tests"""
        tests = {}
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        # Test for stationarity (useful for time series)
        if len(numeric_cols) > 0:
            from statsmodels.stats.diagnostic import acorr_ljungbox
            
            stationarity = {}
            for col in numeric_cols[:5]:  # Limit to first 5 columns
                try:
                    result = acorr_ljungbox(self.df[col].dropna(), lags=10, return_df=True)
                    stationarity[col] = {
                        'ljung_box_stat': round(result['lb_stat'].mean(), 4),
                        'p_value': round(result['lb_pvalue'].mean(), 4)
                    }
                except:
                    pass
            
            tests['stationarity'] = stationarity
        
        self.results['statistical_tests'] = tests
    
    def _display_results_table(self):
        """Display all results in a comprehensive table"""
        
        # Prepare table data
        table_data = []
        
        # Dataset Overview Section
        table_data.append(['='*30, '='*50])
        table_data.append(['DATASET OVERVIEW', ''])
        table_data.append(['-'*30, '-'*50])
        
        for key, value in self.results.get('overview', {}).items():
            table_data.append([key, str(value)])
        
        # Univariate Analysis Section
        table_data.append(['='*30, '='*50])
        table_data.append(['UNIVARIATE ANALYSIS', ''])
        table_data.append(['-'*30, '-'*50])
        
        for col, info in list(self.results.get('univariate', {}).items())[:10]:  # Show first 10
            table_data.append([f'Column: {col}', ''])
            for key, value in list(info.items())[:8]:  # Limit displayed items
                table_data.append([f'  {key}', str(value)])
            table_data.append(['', ''])
        
        # Multivariate Analysis Section
        table_data.append(['='*30, '='*50])
        table_data.append(['MULTIVARIATE ANALYSIS', ''])
        table_data.append(['-'*30, '-'*50])
        
        multivariate = self.results.get('multivariate', {})
        if 'strong_correlations' in multivariate:
            table_data.append(['Strong Correlations (>0.7):', ''])
            for corr in multivariate['strong_correlations'][:5]:  # Show top 5
                table_data.append([f"  {corr['var1']} vs {corr['var2']}", f"{corr['correlation']}"])
        
        if 'avg_correlation' in multivariate:
            table_data.append(['Average Correlation', str(multivariate['avg_correlation'])])
        
        # Correlation Analysis Section
        table_data.append(['='*30, '='*50])
        table_data.append(['CORRELATION ANALYSIS', ''])
        table_data.append(['-'*30, '-'*50])
        
        correlation = self.results.get('correlation', {})
        for key, value in correlation.items():
            if not isinstance(value, dict):
                table_data.append([key, str(value)])
        
        if self.target and 'target_correlations' in correlation:
            table_data.append([f'Target ({self.target}) Correlations:', ''])
            for col, corr_vals in list(correlation['target_correlations'].items())[:5]:
                table_data.append([f"  {col}", f"Pearson: {corr_vals['pearson']}, Spearman: {corr_vals['spearman']}"])
        
        # Causation Analysis Section
        if self.target:
            table_data.append(['='*30, '='*50])
            table_data.append(['CAUSATION ANALYSIS', ''])
            table_data.append(['-'*30, '-'*50])
            
            causation = self.results.get('causation', {})
            if 'target_type' in causation:
                table_data.append(['Target Type', causation['target_type']])
                
                if 'anova_tests' in causation and causation['anova_tests']:
                    table_data.append(['ANOVA Tests:', ''])
                    for col, test in list(causation['anova_tests'].items())[:5]:
                        table_data.append([f"  {col}", f"F={test['f_statistic']}, p={test['p_value']}, Sig={test['significant']}"])
                
                if 'chi_square_tests' in causation and causation['chi_square_tests']:
                    table_data.append(['Chi-Square Tests:', ''])
                    for col, test in list(causation['chi_square_tests'].items())[:5]:
                        table_data.append([f"  {col}", f"χ²={test['chi2']}, p={test['p_value']}, Sig={test['significant']}"])
        
        # Statistical Tests Section
        table_data.append(['='*30, '='*50])
        table_data.append(['STATISTICAL TESTS', ''])
        table_data.append(['-'*30, '-'*50])
        
        tests = self.results.get('statistical_tests', {})
        if 'stationarity' in tests and tests['stationarity']:
            table_data.append(['Stationarity Tests:', ''])
            for col, test in tests['stationarity'].items():
                table_data.append([f"  {col}", f"LB Stat={test['ljung_box_stat']}, p={test['p_value']}"])
        
        # Add footer messages
        table_data.append(['='*30, '='*50])
        table_data.append(['', ''])
        table_data.append(['', 'Made With Love : Louati Mahdi'])
        table_data.append(['', 'Feel free to share the library and my github'])
        table_data.append(['', 'account to your friends'])
        table_data.append(['='*30, '='*50])
        
        # Display table
        print(tabulate(table_data, headers=['Analysis Type', 'Results'], 
                      tablefmt='grid', maxcolwidths=[30, 50]))
        
        return table_data
    
    def quick_report(self) -> str:
        """Generate a quick text report of the analysis"""
        report = []
        report.append("\n" + "="*80)
        report.append("AUTO_LM - QUICK EDA REPORT")
        report.append("="*80 + "\n")
        
        # Perform analysis
        self.analyze()
        
        # Summary statistics
        report.append("\nKEY INSIGHTS:")
        report.append("-" * 40)
        
        overview = self.results.get('overview', {})
        report.append(f"• Dataset has {overview.get('Total Rows', 'N/A')} rows and {overview.get('Total Columns', 'N/A')} columns")
        report.append(f"• Missing data: {overview.get('Missing Percentage', 'N/A')}%")
        report.append(f"• Duplicate rows: {overview.get('Duplicate Rows', 'N/A')}")
        
        multivariate = self.results.get('multivariate', {})
        if 'strong_correlations' in multivariate and multivariate['strong_correlations']:
            report.append(f"• Found {len(multivariate['strong_correlations'])} strong correlations (>0.7)")
        
        report.append("\n" + "="*80)
        report.append("Made With Love : Louati Mahdi")
        report.append("Feel free to share the library and my github account to your friends")
        report.append("="*80 + "\n")
        
        return "\n".join(report)