"""
Python Automation Toolkit
Day 2 of 30-Day Challenge

A collection of 5 practical automation scripts that demonstrate
how to reduce manual work by 60% - based on real Virtusa experience.

Author: Meghana Mareedu
GitHub: https://github.com/MeghanaMareedu13
"""

from file_organizer import FileOrganizer
from data_cleaner import DataCleaner
from report_generator import ReportGenerator
from email_automator import EmailAutomator
from backup_manager import BackupManager

__version__ = "1.0.0"
__author__ = "Meghana Mareedu"

# Quick usage examples
if __name__ == "__main__":
    print("🚀 Python Automation Toolkit")
    print("=" * 40)
    print("\nAvailable Tools:")
    print("1. FileOrganizer - Organize files by type/date")
    print("2. DataCleaner - Clean and validate CSV data")
    print("3. ReportGenerator - Generate Excel/PDF reports")
    print("4. EmailAutomator - Send automated emails")
    print("5. BackupManager - Automated backup system")
    print("\nRun individual scripts for demos!")
