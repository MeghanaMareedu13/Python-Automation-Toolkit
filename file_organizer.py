"""
File Organizer - Automatically organize files by type or date
Part of Python Automation Toolkit | Day 2 of 30-Day Challenge

This script demonstrates how automation can reduce manual file
organization work by 60%+ in enterprise environments.

Author: Meghana Mareedu
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class FileOrganizer:
    """
    Automatically organize files in a directory by type or date.
    
    Features:
    - Organize by file extension (images, documents, videos, etc.)
    - Organize by creation/modification date
    - Undo capability with operation logging
    - Dry-run mode to preview changes
    """
    
    # File type categories
    CATEGORIES = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
        'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.sql', '.json', '.xml'],
        'Data': ['.csv', '.json', '.xml', '.yaml', '.yml', '.db', '.sqlite'],
    }
    
    def __init__(self, source_dir: str):
        """Initialize with source directory path."""
        self.source_dir = Path(source_dir)
        self.operations_log = []
        
        if not self.source_dir.exists():
            raise ValueError(f"Directory does not exist: {source_dir}")
    
    def organize_by_type(self, dry_run: bool = False) -> dict:
        """
        Organize files into folders based on file type.
        
        Args:
            dry_run: If True, only show what would be done without moving files
            
        Returns:
            Dictionary with category names and list of files moved
        """
        results = defaultdict(list)
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Organizing files in: {self.source_dir}")
        print("=" * 50)
        
        for file_path in self.source_dir.iterdir():
            if file_path.is_file():
                category = self._get_category(file_path.suffix.lower())
                
                if category:
                    dest_folder = self.source_dir / category
                    dest_path = dest_folder / file_path.name
                    
                    if not dry_run:
                        dest_folder.mkdir(exist_ok=True)
                        shutil.move(str(file_path), str(dest_path))
                        self.operations_log.append({
                            'action': 'move',
                            'from': str(file_path),
                            'to': str(dest_path),
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    results[category].append(file_path.name)
                    print(f"  {'Would move' if dry_run else 'Moved'}: {file_path.name} → {category}/")
        
        self._print_summary(results)
        return dict(results)
    
    def organize_by_date(self, date_format: str = "%Y-%m", dry_run: bool = False) -> dict:
        """
        Organize files into folders based on modification date.
        
        Args:
            date_format: Format for folder names (default: YYYY-MM)
            dry_run: If True, only show what would be done
            
        Returns:
            Dictionary with date folders and list of files moved
        """
        results = defaultdict(list)
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Organizing files by date in: {self.source_dir}")
        print("=" * 50)
        
        for file_path in self.source_dir.iterdir():
            if file_path.is_file():
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                folder_name = mod_time.strftime(date_format)
                
                dest_folder = self.source_dir / folder_name
                dest_path = dest_folder / file_path.name
                
                if not dry_run:
                    dest_folder.mkdir(exist_ok=True)
                    shutil.move(str(file_path), str(dest_path))
                    self.operations_log.append({
                        'action': 'move',
                        'from': str(file_path),
                        'to': str(dest_path),
                        'timestamp': datetime.now().isoformat()
                    })
                
                results[folder_name].append(file_path.name)
                print(f"  {'Would move' if dry_run else 'Moved'}: {file_path.name} → {folder_name}/")
        
        self._print_summary(results)
        return dict(results)
    
    def undo_last_operation(self) -> bool:
        """Undo the last file move operation."""
        if not self.operations_log:
            print("No operations to undo.")
            return False
        
        last_op = self.operations_log.pop()
        if last_op['action'] == 'move':
            shutil.move(last_op['to'], last_op['from'])
            print(f"Undone: {last_op['to']} → {last_op['from']}")
            return True
        return False
    
    def _get_category(self, extension: str) -> str:
        """Get category name for a file extension."""
        for category, extensions in self.CATEGORIES.items():
            if extension in extensions:
                return category
        return 'Other'
    
    def _print_summary(self, results: dict) -> None:
        """Print organization summary."""
        print("\n" + "=" * 50)
        print("📊 Summary:")
        total = 0
        for category, files in sorted(results.items()):
            count = len(files)
            total += count
            print(f"  {category}: {count} files")
        print(f"\n  Total: {total} files organized")
        print("=" * 50)


# Demo usage
if __name__ == "__main__":
    import tempfile
    
    print("🗂️ File Organizer Demo")
    print("=" * 50)
    
    # Create demo directory with sample files
    with tempfile.TemporaryDirectory() as temp_dir:
        demo_files = [
            'report.pdf', 'photo.jpg', 'data.csv', 'script.py',
            'video.mp4', 'music.mp3', 'archive.zip', 'notes.txt'
        ]
        
        for filename in demo_files:
            Path(temp_dir, filename).touch()
        
        print(f"\nCreated demo files in: {temp_dir}")
        
        # Initialize organizer
        organizer = FileOrganizer(temp_dir)
        
        # Dry run first
        print("\n📋 Dry Run (Preview):")
        organizer.organize_by_type(dry_run=True)
        
        # Actual organization
        print("\n✅ Actual Organization:")
        results = organizer.organize_by_type(dry_run=False)
        
        print("\n🎉 Demo complete!")
