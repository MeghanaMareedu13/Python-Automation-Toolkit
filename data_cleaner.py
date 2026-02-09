"""
Data Cleaner - Automated data cleaning and validation pipeline
Part of Python Automation Toolkit | Day 2 of 30-Day Challenge

Demonstrates enterprise-grade data cleaning that saved 60% manual work
at Virtusa by automating repetitive data processing tasks.

Author: Meghana Mareedu
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Callable
import re


class DataCleaner:
    """
    Automated data cleaning pipeline for CSV/Excel files.
    
    Features:
    - Handle missing values (drop, fill, interpolate)
    - Remove duplicates with customizable strategies
    - Data type conversion and validation
    - Outlier detection and handling
    - Standardize text fields (case, whitespace, special chars)
    - Generate cleaning report
    """
    
    def __init__(self, data: pd.DataFrame = None):
        """Initialize with optional DataFrame."""
        self.df = data
        self.original_shape = None
        self.cleaning_log = []
        
    def load_csv(self, filepath: str, **kwargs) -> 'DataCleaner':
        """Load data from CSV file."""
        self.df = pd.read_csv(filepath, **kwargs)
        self.original_shape = self.df.shape
        self._log(f"Loaded {self.original_shape[0]} rows, {self.original_shape[1]} columns")
        return self
    
    def load_excel(self, filepath: str, **kwargs) -> 'DataCleaner':
        """Load data from Excel file."""
        self.df = pd.read_excel(filepath, **kwargs)
        self.original_shape = self.df.shape
        self._log(f"Loaded {self.original_shape[0]} rows, {self.original_shape[1]} columns")
        return self
    
    # ===== MISSING VALUES =====
    
    def handle_missing(self, strategy: str = 'drop', columns: List[str] = None, 
                       fill_value: any = None) -> 'DataCleaner':
        """
        Handle missing values in the dataset.
        
        Args:
            strategy: 'drop', 'fill', 'ffill', 'bfill', 'mean', 'median', 'mode'
            columns: Specific columns to process (None = all)
            fill_value: Value to use when strategy='fill'
        """
        before = self.df.isna().sum().sum()
        cols = columns or self.df.columns.tolist()
        
        if strategy == 'drop':
            self.df = self.df.dropna(subset=cols)
        elif strategy == 'fill':
            self.df[cols] = self.df[cols].fillna(fill_value)
        elif strategy == 'ffill':
            self.df[cols] = self.df[cols].ffill()
        elif strategy == 'bfill':
            self.df[cols] = self.df[cols].bfill()
        elif strategy == 'mean':
            for col in cols:
                if self.df[col].dtype in ['int64', 'float64']:
                    self.df[col] = self.df[col].fillna(self.df[col].mean())
        elif strategy == 'median':
            for col in cols:
                if self.df[col].dtype in ['int64', 'float64']:
                    self.df[col] = self.df[col].fillna(self.df[col].median())
        elif strategy == 'mode':
            for col in cols:
                self.df[col] = self.df[col].fillna(self.df[col].mode().iloc[0] if not self.df[col].mode().empty else None)
        
        after = self.df.isna().sum().sum()
        self._log(f"Missing values: {before} → {after} (strategy: {strategy})")
        return self
    
    # ===== DUPLICATES =====
    
    def remove_duplicates(self, subset: List[str] = None, keep: str = 'first') -> 'DataCleaner':
        """
        Remove duplicate rows.
        
        Args:
            subset: Columns to consider for duplicate detection
            keep: 'first', 'last', or False (remove all duplicates)
        """
        before = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        after = len(self.df)
        self._log(f"Duplicates removed: {before - after} rows")
        return self
    
    # ===== DATA TYPES =====
    
    def convert_types(self, type_map: Dict[str, str]) -> 'DataCleaner':
        """
        Convert column data types.
        
        Args:
            type_map: Dictionary of {column: dtype}
        """
        for col, dtype in type_map.items():
            if col in self.df.columns:
                try:
                    if dtype == 'datetime':
                        self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                    else:
                        self.df[col] = self.df[col].astype(dtype)
                    self._log(f"Converted '{col}' to {dtype}")
                except Exception as e:
                    self._log(f"Failed to convert '{col}': {e}")
        return self
    
    # ===== TEXT STANDARDIZATION =====
    
    def standardize_text(self, columns: List[str], 
                         lowercase: bool = True,
                         strip_whitespace: bool = True,
                         remove_special: bool = False) -> 'DataCleaner':
        """
        Standardize text columns.
        
        Args:
            columns: List of columns to standardize
            lowercase: Convert to lowercase
            strip_whitespace: Remove leading/trailing whitespace
            remove_special: Remove special characters
        """
        for col in columns:
            if col in self.df.columns and self.df[col].dtype == 'object':
                if strip_whitespace:
                    self.df[col] = self.df[col].str.strip()
                if lowercase:
                    self.df[col] = self.df[col].str.lower()
                if remove_special:
                    self.df[col] = self.df[col].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
                self._log(f"Standardized text in '{col}'")
        return self
    
    # ===== OUTLIERS =====
    
    def handle_outliers(self, columns: List[str], method: str = 'iqr', 
                        action: str = 'clip') -> 'DataCleaner':
        """
        Detect and handle outliers.
        
        Args:
            columns: Numeric columns to check
            method: 'iqr' (Interquartile Range) or 'zscore'
            action: 'clip' (cap values) or 'drop' (remove rows)
        """
        for col in columns:
            if col in self.df.columns and self.df[col].dtype in ['int64', 'float64']:
                if method == 'iqr':
                    Q1 = self.df[col].quantile(0.25)
                    Q3 = self.df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower = Q1 - 1.5 * IQR
                    upper = Q3 + 1.5 * IQR
                elif method == 'zscore':
                    mean = self.df[col].mean()
                    std = self.df[col].std()
                    lower = mean - 3 * std
                    upper = mean + 3 * std
                
                outliers = ((self.df[col] < lower) | (self.df[col] > upper)).sum()
                
                if action == 'clip':
                    self.df[col] = self.df[col].clip(lower, upper)
                elif action == 'drop':
                    self.df = self.df[(self.df[col] >= lower) & (self.df[col] <= upper)]
                
                self._log(f"Outliers in '{col}': {outliers} ({action}ed, method: {method})")
        return self
    
    # ===== VALIDATION =====
    
    def validate(self, rules: Dict[str, Callable]) -> Dict[str, bool]:
        """
        Validate data against custom rules.
        
        Args:
            rules: Dictionary of {rule_name: validation_function}
            
        Returns:
            Dictionary of validation results
        """
        results = {}
        for rule_name, rule_func in rules.items():
            try:
                results[rule_name] = rule_func(self.df)
                status = "✅ PASS" if results[rule_name] else "❌ FAIL"
                self._log(f"Validation '{rule_name}': {status}")
            except Exception as e:
                results[rule_name] = False
                self._log(f"Validation '{rule_name}': ❌ ERROR - {e}")
        return results
    
    # ===== OUTPUT =====
    
    def save(self, filepath: str, index: bool = False) -> 'DataCleaner':
        """Save cleaned data to file."""
        path = Path(filepath)
        if path.suffix == '.csv':
            self.df.to_csv(filepath, index=index)
        elif path.suffix in ['.xlsx', '.xls']:
            self.df.to_excel(filepath, index=index)
        self._log(f"Saved to {filepath}")
        return self
    
    def get_report(self) -> str:
        """Generate cleaning report."""
        report = [
            "=" * 50,
            "📊 DATA CLEANING REPORT",
            "=" * 50,
            f"\nOriginal Shape: {self.original_shape}",
            f"Final Shape: {self.df.shape}",
            f"Rows Changed: {self.original_shape[0] - self.df.shape[0]}",
            "\n📋 Operations Log:",
            "-" * 30
        ]
        for i, log in enumerate(self.cleaning_log, 1):
            report.append(f"  {i}. {log}")
        report.append("=" * 50)
        return "\n".join(report)
    
    def _log(self, message: str) -> None:
        """Add entry to cleaning log."""
        self.cleaning_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")


# Demo usage
if __name__ == "__main__":
    print("🧹 Data Cleaner Demo")
    print("=" * 50)
    
    # Create sample messy data
    sample_data = pd.DataFrame({
        'Name': ['  John Doe  ', 'JANE SMITH', 'john doe', 'Bob Wilson', None],
        'Email': ['john@email.com', 'jane@email.com', 'john@email.com', 'bob@email.com', 'invalid'],
        'Age': [25, 30, 25, 150, 35],  # 150 is an outlier
        'Salary': [50000, None, 50000, 75000, 60000],
        'Join_Date': ['2023-01-15', '2023-02-20', '2023-01-15', '2023-03-10', '2023-04-05']
    })
    
    print("\n📥 Original Data:")
    print(sample_data)
    
    # Initialize cleaner and run pipeline
    cleaner = DataCleaner(sample_data)
    cleaner.original_shape = sample_data.shape
    
    cleaner \
        .handle_missing(strategy='drop') \
        .remove_duplicates(subset=['Name', 'Email']) \
        .standardize_text(['Name'], lowercase=True, strip_whitespace=True) \
        .handle_outliers(['Age'], method='iqr', action='clip') \
        .handle_missing(strategy='median', columns=['Salary'])
    
    print("\n✅ Cleaned Data:")
    print(cleaner.df)
    
    print(cleaner.get_report())
