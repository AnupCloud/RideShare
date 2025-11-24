import pandas as pd
import numpy as np
from scipy import stats

def analyze_missing_values(df: pd.DataFrame) -> dict:
    """
    Comprehensive missing value analysis
    
    Returns:
    - missing_summary: {column: {count, percentage, action}}
    - columns_to_drop: list of columns with > 30% missing
    - imputation_strategy: {column: method}
    """
    total_rows = len(df)
    missing_summary = {}
    columns_to_drop = []
    imputation_strategy = {}
    
    for col in df.columns:
        missing_count = df[col].isna().sum()
        missing_pct = (missing_count / total_rows) * 100
        
        if missing_count > 0:
            # Determine action
            if missing_pct > 30:
                action = "DROP_COLUMN"
                columns_to_drop.append(col)
            elif df[col].dtype in ['int64', 'float64']:
                action = "IMPUTE_MEDIAN"
                imputation_strategy[col] = 'median'
            else:
                action = "IMPUTE_MODE"
                imputation_strategy[col] = 'mode'
            
            missing_summary[col] = {
                'count': int(missing_count),
                'percentage': float(missing_pct),
                'action': action,
                'dtype': str(df[col].dtype)
            }
    
    return {
        'missing_summary': missing_summary,
        'columns_to_drop': columns_to_drop,
        'imputation_strategy': imputation_strategy,
        'total_columns': len(df.columns),
        'columns_with_missing': len(missing_summary)
    }

def detect_outliers(df: pd.DataFrame, method='IQR') -> dict:
    """
    Detect outliers in numerical columns
    
    Methods: 
    - IQR: Interquartile Range (Q1 - 1.5*IQR, Q3 + 1.5*IQR)
    - Z-score: |z| > 3
    
    Returns:
    - outliers_by_column: {column: {count, percentage, indices}}
    - outlier_summary: total outliers, affected columns
    """
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    outliers_by_column = {}
    total_outliers = 0
    
    for col in numerical_cols:
        col_data = df[col].dropna()
        
        if len(col_data) == 0:
            continue
        
        if method == 'IQR':
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = (col_data < lower_bound) | (col_data > upper_bound)
        
        elif method == 'Z-score':
            z_scores = np.abs(stats.zscore(col_data))
            outliers = z_scores > 3
        
        outlier_count = outliers.sum()
        
        if outlier_count > 0:
            outliers_by_column[col] = {
                'count': int(outlier_count),
                'percentage': float((outlier_count / len(col_data)) * 100),
                'method': method,
                'bounds': {
                    'lower': float(lower_bound) if method == 'IQR' else None,
                    'upper': float(upper_bound) if method == 'IQR' else None
                } if method == 'IQR' else None
            }
            total_outliers += outlier_count
    
    return {
        'outliers_by_column': outliers_by_column,
        'total_outliers': int(total_outliers),
        'affected_columns': len(outliers_by_column),
        'method_used': method
    }

def treat_outliers(df: pd.DataFrame, treatment='cap', method='IQR') -> pd.DataFrame:
    """
    Treat outliers in numerical columns
    
    Treatments:
    - cap: Replace outliers with bounds (IQR method)
    - remove: Remove rows with outliers
    - transform: Log transformation
    
    Returns: cleaned DataFrame
    """
    df_clean = df.copy()
    numerical_cols = df_clean.select_dtypes(include=[np.number]).columns
    
    for col in numerical_cols:
        col_data = df_clean[col].dropna()
        
        if len(col_data) == 0:
            continue
        
        if method == 'IQR':
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            if treatment == 'cap':
                df_clean[col] = df_clean[col].clip(lower=lower_bound, upper=upper_bound)
            elif treatment == 'remove':
                outliers = (df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)
                df_clean = df_clean[~outliers]
    
    return df_clean

def get_data_quality_report(df: pd.DataFrame) -> dict:
    """
    Comprehensive data quality report
    
    Returns:
    - missing_values: analysis from analyze_missing_values
    - outliers: analysis from detect_outliers
    - data_types: summary of column types
    - duplicate_rows: count and percentage
    - value_range_validation: for numerical columns
    """
    missing_analysis = analyze_missing_values(df)
    outlier_analysis = detect_outliers(df, method='IQR')
    
    # Data type summary
    dtype_summary = df.dtypes.value_counts().to_dict()
    dtype_summary = {str(k): int(v) for k, v in dtype_summary.items()}
    
    # Duplicate rows
    duplicate_count = df.duplicated().sum()
    duplicate_pct = (duplicate_count / len(df)) * 100
    
    # Value range validation for key numerical columns
    value_ranges = {}
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numerical_cols:
        if df[col].notna().any():
            value_ranges[col] = {
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'mean': float(df[col].mean()),
                'median': float(df[col].median()),
                'std': float(df[col].std())
            }
    
    return {
        'dataset_info': {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': float(df.memory_usage(deep=True).sum() / 1024**2)
        },
        'missing_values': missing_analysis,
        'outliers': outlier_analysis,
        'data_types': dtype_summary,
        'duplicates': {
            'count': int(duplicate_count),
            'percentage': float(duplicate_pct)
        },
        'value_ranges': value_ranges
    }
