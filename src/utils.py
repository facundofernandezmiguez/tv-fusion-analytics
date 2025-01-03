"""
Utility functions for TV Fusion Analysis Tools.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Union, Optional

def add_market_names(df: pd.DataFrame, market_codes: pd.DataFrame) -> pd.DataFrame:
    """
    Add market names to a DataFrame and reorder columns.
    
    Args:
        df: Input DataFrame with 'market' column
        market_codes: DataFrame containing market codes and names
    
    Returns:
        DataFrame with added market names and reordered columns
    """
    df = df.merge(market_codes[['market', 'market name']], on='market', how='left')
    new_order = ['market name', 'market'] + [
        col for col in df.columns if col not in ['market name', 'market']
    ]
    return df.reindex(columns=new_order)

def apply_excel_formatting(
    worksheet: 'xlsxwriter.worksheet.Worksheet',
    column_formats: Dict[str, Dict],
    start_row: int = 2,
    end_row: int = 1000
) -> None:
    """
    Apply conditional formatting to Excel worksheet columns.
    
    Args:
        worksheet: Excel worksheet object
        column_formats: Dictionary mapping column letters to format specifications
        start_row: Starting row for formatting
        end_row: Ending row for formatting
    """
    for col, format_spec in column_formats.items():
        worksheet.conditional_format(
            f'{col}{start_row}:{col}{end_row}',
            format_spec
        )

def calculate_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate basic statistics for a DataFrame.
    
    Args:
        df: Input DataFrame
    
    Returns:
        DataFrame with added statistics rows
    """
    df.loc['Average'] = df.mean().round(1)
    df.loc['Min'] = df.min()
    df.loc['Max'] = df.max()
    df.loc['St. Dev'] = df.std().round(1)
    
    # Reorder rows to put statistics at top
    row_order = ['Average', 'Min', 'Max', 'St. Dev'] + list(df.index[:-4])
    return df.reindex(row_order)

def categorize_change(
    value: float,
    threshold: float,
    increase_label: str = 'increase',
    decrease_label: str = 'decrease',
    no_change_label: str = 'no change'
) -> str:
    """
    Categorize a change value based on a threshold.
    
    Args:
        value: Change value to categorize
        threshold: Threshold for significance
        increase_label: Label for increase
        decrease_label: Label for decrease
        no_change_label: Label for no change
    
    Returns:
        Category label
    """
    if pd.isna(value):
        return no_change_label
    elif value > threshold:
        return increase_label
    elif value < -threshold:
        return decrease_label
    else:
        return no_change_label

def safe_numeric_conversion(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Safely convert a column to numeric type.
    
    Args:
        df: Input DataFrame
        column: Column name to convert
    
    Returns:
        DataFrame with converted column
    """
    df = df.copy()
    df[column] = pd.to_numeric(df[column], errors='coerce')
    return df

def create_pivot_table(
    df: pd.DataFrame,
    index: Union[str, List[str]],
    columns: Union[str, List[str]],
    values: str,
    aggfunc: str = 'mean',
    round_digits: Optional[int] = None
) -> pd.DataFrame:
    """
    Create a pivot table with optional rounding.
    
    Args:
        df: Input DataFrame
        index: Index columns
        columns: Column names for pivot
        values: Values column
        aggfunc: Aggregation function
        round_digits: Number of decimal places for rounding
    
    Returns:
        Pivot table DataFrame
    """
    pivot = pd.pivot_table(
        df,
        index=index,
        columns=columns,
        values=values,
        aggfunc=aggfunc
    )
    
    if round_digits is not None:
        pivot = pivot.round(round_digits)
    
    return pivot
