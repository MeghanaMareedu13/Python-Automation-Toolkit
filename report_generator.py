"""
Report Generator - Automated report generation in multiple formats
Part of Python Automation Toolkit | Day 2 of 30-Day Challenge

Automates the creation of Excel and text reports from data,
saving hours of manual formatting work.

Author: Meghana Mareedu
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json


class ReportGenerator:
    """
    Generate professional reports from data in multiple formats.
    
    Features:
    - Excel reports with formatting
    - Summary statistics
    - Text/Markdown reports
    - JSON export
    - Customizable templates
    """
    
    def __init__(self, data: pd.DataFrame, title: str = "Data Report"):
        """Initialize with DataFrame and report title."""
        self.df = data
        self.title = title
        self.generated_at = datetime.now()
        self.metadata = {}
    
    def add_metadata(self, key: str, value: any) -> 'ReportGenerator':
        """Add custom metadata to the report."""
        self.metadata[key] = value
        return self
    
    def generate_summary(self) -> Dict:
        """Generate summary statistics."""
        summary = {
            'title': self.title,
            'generated_at': self.generated_at.isoformat(),
            'row_count': len(self.df),
            'column_count': len(self.df.columns),
            'columns': self.df.columns.tolist(),
            'data_types': self.df.dtypes.astype(str).to_dict(),
            'missing_values': self.df.isna().sum().to_dict(),
            'memory_usage': f"{self.df.memory_usage(deep=True).sum() / 1024:.2f} KB"
        }
        
        # Numeric column statistics
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            summary['numeric_stats'] = self.df[numeric_cols].describe().to_dict()
        
        summary['metadata'] = self.metadata
        return summary
    
    def to_excel(self, filepath: str, include_summary: bool = True) -> str:
        """
        Generate Excel report with optional summary sheet.
        
        Args:
            filepath: Output file path
            include_summary: Include a summary statistics sheet
        """
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main data sheet
            self.df.to_excel(writer, sheet_name='Data', index=False)
            
            if include_summary:
                # Summary sheet
                summary = self.generate_summary()
                summary_df = pd.DataFrame([
                    ['Report Title', summary['title']],
                    ['Generated At', summary['generated_at']],
                    ['Total Rows', summary['row_count']],
                    ['Total Columns', summary['column_count']],
                    ['Memory Usage', summary['memory_usage']],
                ], columns=['Metric', 'Value'])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Column info sheet
                col_info = pd.DataFrame({
                    'Column': self.df.columns,
                    'Data Type': self.df.dtypes.astype(str).values,
                    'Missing Values': self.df.isna().sum().values,
                    'Unique Values': [self.df[col].nunique() for col in self.df.columns]
                })
                col_info.to_excel(writer, sheet_name='Column Info', index=False)
        
        print(f"✅ Excel report saved: {filepath}")
        return filepath
    
    def to_markdown(self, filepath: str = None) -> str:
        """
        Generate Markdown report.
        
        Args:
            filepath: Optional output file path
            
        Returns:
            Markdown string
        """
        summary = self.generate_summary()
        
        lines = [
            f"# {self.title}",
            "",
            f"**Generated:** {summary['generated_at']}",
            "",
            "## Overview",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Rows | {summary['row_count']:,} |",
            f"| Columns | {summary['column_count']} |",
            f"| Memory | {summary['memory_usage']} |",
            "",
            "## Columns",
            "",
            "| Column | Type | Missing | Unique |",
            "|--------|------|---------|--------|",
        ]
        
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            missing = self.df[col].isna().sum()
            unique = self.df[col].nunique()
            lines.append(f"| {col} | {dtype} | {missing} | {unique} |")
        
        # Numeric stats
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            lines.extend([
                "",
                "## Numeric Statistics",
                "",
                self.df[numeric_cols].describe().to_markdown()
            ])
        
        # Data preview
        lines.extend([
            "",
            "## Data Preview (First 10 rows)",
            "",
            self.df.head(10).to_markdown(index=False)
        ])
        
        markdown = "\n".join(lines)
        
        if filepath:
            Path(filepath).write_text(markdown)
            print(f"✅ Markdown report saved: {filepath}")
        
        return markdown
    
    def to_json(self, filepath: str = None, orient: str = 'records') -> str:
        """
        Export data and summary as JSON.
        
        Args:
            filepath: Optional output file path
            orient: DataFrame orientation for JSON
        """
        output = {
            'summary': self.generate_summary(),
            'data': json.loads(self.df.to_json(orient=orient))
        }
        
        json_str = json.dumps(output, indent=2, default=str)
        
        if filepath:
            Path(filepath).write_text(json_str)
            print(f"✅ JSON report saved: {filepath}")
        
        return json_str
    
    def to_text(self, filepath: str = None) -> str:
        """Generate plain text report."""
        summary = self.generate_summary()
        
        lines = [
            "=" * 60,
            f" {self.title.upper()}",
            "=" * 60,
            "",
            f"Generated: {summary['generated_at']}",
            "",
            "OVERVIEW",
            "-" * 40,
            f"  Rows: {summary['row_count']:,}",
            f"  Columns: {summary['column_count']}",
            f"  Memory: {summary['memory_usage']}",
            "",
            "COLUMNS",
            "-" * 40,
        ]
        
        for col in self.df.columns:
            lines.append(f"  • {col} ({self.df[col].dtype})")
        
        lines.extend([
            "",
            "DATA PREVIEW",
            "-" * 40,
            self.df.head(5).to_string(),
            "",
            "=" * 60
        ])
        
        text = "\n".join(lines)
        
        if filepath:
            Path(filepath).write_text(text)
            print(f"✅ Text report saved: {filepath}")
        
        return text


# Demo usage
if __name__ == "__main__":
    print("📊 Report Generator Demo")
    print("=" * 50)
    
    # Sample data
    data = pd.DataFrame({
        'Product': ['Widget A', 'Widget B', 'Gadget X', 'Gadget Y', 'Tool Z'],
        'Category': ['Widgets', 'Widgets', 'Gadgets', 'Gadgets', 'Tools'],
        'Price': [29.99, 39.99, 149.99, 199.99, 79.99],
        'Stock': [150, 75, 30, 25, 100],
        'Rating': [4.5, 4.2, 4.8, 4.6, 4.0]
    })
    
    # Generate reports
    report = ReportGenerator(data, "Product Inventory Report")
    report.add_metadata('department', 'Sales')
    report.add_metadata('quarter', 'Q1 2026')
    
    # Print markdown preview
    print("\n📝 Markdown Report Preview:")
    print(report.to_markdown())
    
    print("\n🎉 Report Generator Demo Complete!")
