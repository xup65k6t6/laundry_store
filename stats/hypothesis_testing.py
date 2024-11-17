import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import statsmodels.api as sm
from typing import Union, Tuple, Dict
import sys
from pathlib import Path
# Dynamically find the project root and add it to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
from data_processing.data_cleaning import read_df_from_db

class NormalityAnalyzer:
    """
    A class to analyze the normality of data through various statistical methods and visualizations.
    """
    
    def __init__(self, data: Union[pd.Series, np.ndarray], column_name: str = "Value"):
        """
        Initialize the analyzer with data.
        
        Parameters:
        -----------
        data : Union[pd.Series, np.ndarray]
            The data to analyze
        column_name : str
            Name of the data column for plotting
        """
        self.data = pd.Series(data) if isinstance(data, np.ndarray) else data
        self.column_name = column_name
    
    def plot_normality_checks(self) -> None:
        """
        Create visual plots to check normality:
        1. Histogram with normal curve overlay
        2. Q-Q plot
        """
        # Create a figure with two subplots side by side
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Histogram with normal curve
        mu, sigma = stats.norm.fit(self.data)
        x = np.linspace(self.data.min(), self.data.max(), 100)
        
        ax1.hist(self.data, bins='auto', density=True, alpha=0.7, color='skyblue')
        ax1.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', lw=2, 
                label=f'Normal(μ={mu:.1f}, σ={sigma:.1f})')
        ax1.set_title(f'Histogram of {self.column_name} with Normal Curve')
        ax1.set_xlabel(self.column_name)
        ax1.set_ylabel('Density')
        ax1.legend()
        
        # Q-Q plot
        sm.graphics.qqplot(self.data, line='45', ax=ax2)
        ax2.set_title('Q-Q Plot')
        
        plt.tight_layout()
        plt.show()
    
    def run_statistical_tests(self) -> Dict[str, Tuple[float, float]]:
        """
        Run multiple statistical tests for normality.
        
        Returns:
        --------
        Dict containing test results with test statistics and p-values
        """
        # Shapiro-Wilk test
        shapiro_stat, shapiro_p = stats.shapiro(self.data)
        
        # D'Agostino-Pearson test
        k2_stat, k2_p = stats.normaltest(self.data)
        
        return {
            'shapiro': (shapiro_stat, shapiro_p),
            'dagostino': (k2_stat, k2_p)
        }
    
    def calculate_shape_statistics(self) -> Dict[str, float]:
        """
        Calculate shape statistics (skewness and kurtosis).
        
        Returns:
        --------
        Dict containing shape statistics
        """
        return {
            'skewness': stats.skew(self.data),
            'kurtosis': stats.kurtosis(self.data)
        }
    
    def print_analysis_results(self) -> None:
        """
        Print comprehensive normality analysis results.
        """
        # Run tests
        test_results = self.run_statistical_tests()
        shape_stats = self.calculate_shape_statistics()
        
        # Print results
        print(f"\nNormality Analysis Results for {self.column_name}")
        print("="*50)
        
        print("\n1. Statistical Tests:")
        print("-"*20)
        
        # Shapiro-Wilk test results
        print("\nShapiro-Wilk test:")
        print(f"Statistic: {test_results['shapiro'][0]:.4f}")
        print(f"P-value: {test_results['shapiro'][1]:.4f}")
        print(f"Interpretation: {'Not normal' if test_results['shapiro'][1] < 0.05 else 'Cannot reject normality'}")
        
        # D'Agostino-Pearson test results
        print("\nD'Agostino-Pearson test:")
        print(f"Statistic: {test_results['dagostino'][0]:.4f}")
        print(f"P-value: {test_results['dagostino'][1]:.4f}")
        print(f"Interpretation: {'Not normal' if test_results['dagostino'][1] < 0.05 else 'Cannot reject normality'}")
        
        print("\n2. Shape Statistics:")
        print("-"*20)
        print(f"Skewness: {shape_stats['skewness']:.4f}")
        print(f"  - Interpretation: {'Symmetric' if abs(shape_stats['skewness']) < 0.5 else 'Right-skewed' if shape_stats['skewness'] > 0 else 'Left-skewed'}")
        print(f"Kurtosis: {shape_stats['kurtosis']:.4f}")
        print(f"  - Interpretation: {'Normal tails' if abs(shape_stats['kurtosis']) < 0.5 else 'Heavy tails' if shape_stats['kurtosis'] > 0 else 'Light tails'}")
        
    def analyze_normality(self) -> None:
        """
        Perform complete normality analysis including plots and statistical tests.
        """
        # Create visualizations
        self.plot_normality_checks()
        
        # Print analysis results
        self.print_analysis_results()

def analyze_cny_sales(df, days_before=14, cny_holiday_days=5):
    """
    Perform hypothesis testing to check if daily sales are significantly higher before Chinese New Year,
    excluding the CNY holiday period itself. Handles transaction-level data by aggregating to daily totals.
    
    Parameters:
    df: DataFrame containing transaction-level sales data
    days_before: Number of days before CNY to consider as 'pre-CNY period'
    cny_holiday_days: Number of CNY holiday days to exclude
    
    Returns:
    dict containing test results and summary statistics
    """
    # Chinese New Year dates for recent years
    cny_dates = {
        2020: '2020-01-25',
        2021: '2021-02-12',
        2022: '2022-02-01',
        2023: '2023-01-22',
        2024: '2024-02-10'
    }
    
    # Ensure Date is datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Aggregate sales by date
    daily_sales = df.groupby('Date')['Amount'].sum().reset_index()
    
    # Create masks for pre-CNY periods and CNY holiday periods
    pre_cny_mask = pd.Series(False, index=daily_sales.index)
    cny_holiday_mask = pd.Series(False, index=daily_sales.index)
    
    for year, cny_date in cny_dates.items():
        cny_datetime = pd.to_datetime(cny_date)
        
        # Define pre-CNY period (ending the day before CNY)
        pre_cny_end = cny_datetime - timedelta(days=1)
        pre_cny_start = pre_cny_end - timedelta(days=days_before-1)
        pre_cny_period = pd.date_range(start=pre_cny_start, end=pre_cny_end)
        
        # Define CNY holiday period
        cny_holiday_period = pd.date_range(start=cny_datetime, 
                                         periods=cny_holiday_days)
        
        # Update masks
        pre_cny_mask |= daily_sales['Date'].isin(pre_cny_period)
        cny_holiday_mask |= daily_sales['Date'].isin(cny_holiday_period)
    
    # Split data into pre-CNY and regular periods
    pre_cny_sales = daily_sales[pre_cny_mask]['Amount']
    regular_sales = daily_sales[~(pre_cny_mask | cny_holiday_mask)]['Amount']
    
    # Perform Mann-Whitney U test
    statistic, p_value = stats.mannwhitneyu(
        pre_cny_sales, 
        regular_sales, 
        alternative='greater'  # Testing if pre-CNY sales are greater
    )
    
    # Calculate daily summary statistics
    results = {
        'pre_cny_daily_mean': pre_cny_sales.mean(),
        'regular_daily_mean': regular_sales.mean(),
        'pre_cny_daily_median': pre_cny_sales.median(),
        'regular_daily_median': regular_sales.median(),
        'pre_cny_daily_std': pre_cny_sales.std(),
        'regular_daily_std': regular_sales.std(),
        'pre_cny_days': len(pre_cny_sales),
        'regular_days': len(regular_sales),
        'percent_difference': ((pre_cny_sales.mean() - regular_sales.mean()) / regular_sales.mean()) * 100,
        'p_value': p_value,
        'statistic': statistic
    }
    
    return results, daily_sales

def print_analysis_results(results):
    """
    Print the analysis results in a readable format.
    """
    print("\nChinese New Year Sales Analysis Results (Daily Aggregated)")
    print("===============================================")
    print(f"Pre-CNY Period Statistics:")
    print(f"- Mean daily sales: {results['pre_cny_daily_mean']:.2f}")
    print(f"- Median daily sales: {results['pre_cny_daily_median']:.2f}")
    print(f"- Daily standard deviation: {results['pre_cny_daily_std']:.2f}")
    print(f"- Number of days: {results['pre_cny_days']}")
    
    print("\nRegular Period Statistics:")
    print(f"- Mean daily sales: {results['regular_daily_mean']:.2f}")
    print(f"- Median daily sales: {results['regular_daily_median']:.2f}")
    print(f"- Daily standard deviation: {results['regular_daily_std']:.2f}")
    print(f"- Number of days: {results['regular_days']}")
    
    print("\nComparison:")
    print(f"- Percentage difference in daily means: {results['percent_difference']:.2f}%")
    print(f"- P-value: {results['p_value']:.4f}")
    print(f"- Statistical significance: {'Significant' if results['p_value'] < 0.05 else 'Not significant'} at α=0.05")

def plot_daily_sales(daily_sales, cny_dates, days_before=14):
    """
    Create a visualization of daily sales with pre-CNY periods highlighted.
    """
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(15, 6))
    plt.plot(daily_sales['Date'], daily_sales['Amount'], label='Daily Sales', alpha=0.6)
    
    # Highlight pre-CNY periods
    for year, cny_date in cny_dates.items():
        cny_datetime = pd.to_datetime(cny_date)
        pre_cny_end = cny_datetime - timedelta(days=1)
        pre_cny_start = pre_cny_end - timedelta(days=days_before-1)
        
        plt.axvspan(pre_cny_start, pre_cny_end, color='yellow', alpha=0.3)
        plt.axvline(cny_datetime, color='red', linestyle='--', alpha=0.5)
    
    plt.title('Daily Sales with Pre-CNY Periods Highlighted')
    plt.xlabel('Date')
    plt.ylabel('Daily Sales Amount')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

def main(db_path:str = 'data/database.db'):
    table_name = 'clean_sales_data'
    df = read_df_from_db(db_path, table_name)

    # Test if Sales is norally distributed
    daily_sales = df.groupby('Date')['Amount'].sum().reset_index()
    analyzer = NormalityAnalyzer(daily_sales['Amount'], column_name='Daily Sales')
    analyzer.analyze_normality()

    # Mann-Whitney U test to check if the sales before Chinese New Year (CNY) are significantly higher
    results, daily_sales = analyze_cny_sales(df, days_before=2, cny_holiday_days=0)
    print_analysis_results(results)
    # Optional: visualize the daily sales pattern
    # cny_dates = {
    #     2023: '2023-01-22',
    #     2024: '2024-02-10'
    # }
    # plot_daily_sales(daily_sales, cny_dates, days_before=2)

if __name__ == "__main__":
    main()