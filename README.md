# 🤖 Python Automation Toolkit

![Day 02](https://img.shields.io/badge/Day-02-purple?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python&logoColor=white)
![Automation](https://img.shields.io/badge/Automation-60%25%20Time%20Saved-green?style=flat)

> **Day 2 of 30-Day Challenge** | Enterprise-grade automation scripts that reduced manual work by 60%

## 🎯 The Problem

In my previous experience, I saw teams spending hours on:
- Manually organizing downloaded files
- Cleaning messy CSV data by hand
- Creating reports in Excel
- Sending repetitive emails
- Managing backups manually

**Solution**: I built automation scripts that handle these tasks in seconds.

## 🛠️ Tools Included

| Script | Purpose | Time Saved |
|--------|---------|------------|
| `file_organizer.py` | Organize files by type/date | 90% |
| `data_cleaner.py` | Clean & validate data | 70% |
| `report_generator.py` | Generate Excel/Markdown reports | 80% |
| `email_automator.py` | Send templated bulk emails | 85% |
| `backup_manager.py` | Automated compressed backups | 95% |

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/MeghanaMareedu13/python-automation.git
cd python-automation

# Install dependencies
pip install -r requirements.txt

# Run any script demo
python file_organizer.py
python data_cleaner.py
python report_generator.py
python email_automator.py
python backup_manager.py
```

## 📖 Usage Examples

### File Organizer
```python
from file_organizer import FileOrganizer

organizer = FileOrganizer("./downloads")
organizer.organize_by_type(dry_run=False)  # Organize by extension
organizer.organize_by_date()  # Or organize by date
```

### Data Cleaner
```python
from data_cleaner import DataCleaner

cleaner = DataCleaner()
cleaner.load_csv("messy_data.csv") \
    .handle_missing(strategy='median') \
    .remove_duplicates() \
    .handle_outliers(['price'], method='iqr') \
    .save("clean_data.csv")

print(cleaner.get_report())
```

### Report Generator
```python
from report_generator import ReportGenerator
import pandas as pd

data = pd.read_csv("sales.csv")
report = ReportGenerator(data, "Q1 Sales Report")
report.to_excel("report.xlsx")
report.to_markdown("report.md")
```

## 🎯 Key Features

- ✅ **Dry-run mode** - Preview before executing
- ✅ **Undo capability** - Reverse operations
- ✅ **Logging** - Track all operations
- ✅ **Validation** - Data integrity checks
- ✅ **Templates** - Reusable configurations

## 👤 Author

**Meghana Mareedu**
- 💼 [LinkedIn](https://linkedin.com/in/meghanagoud13)
- 🐙 [GitHub](https://github.com/MeghanaMareedu13)

---

⭐ **Part of my 30-Day Project Challenge** - Follow for daily projects!

#Python #Automation #DataEngineering #30DayChallenge
