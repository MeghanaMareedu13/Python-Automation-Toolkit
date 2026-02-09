"""
Backup Manager - Automated file backup system
Part of Python Automation Toolkit | Day 2 of 30-Day Challenge

Implements scheduled backups with rotation, compression,
and verification - essential for any production environment.

Author: Meghana Mareedu
"""

import os
import shutil
import hashlib
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json


class BackupManager:
    """
    Automated backup system with compression and rotation.
    
    Features:
    - Full and incremental backups
    - ZIP compression
    - Backup rotation (keep N most recent)
    - Integrity verification with checksums
    - Backup manifest/catalog
    - Restore capability
    """
    
    def __init__(self, source_dir: str, backup_dir: str):
        """
        Initialize backup manager.
        
        Args:
            source_dir: Directory to backup
            backup_dir: Directory to store backups
        """
        self.source_dir = Path(source_dir)
        self.backup_dir = Path(backup_dir)
        self.manifest_file = self.backup_dir / "backup_manifest.json"
        
        # Create backup directory if needed
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create manifest
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict:
        """Load backup manifest from disk."""
        if self.manifest_file.exists():
            return json.loads(self.manifest_file.read_text())
        return {'backups': [], 'settings': {'max_backups': 5}}
    
    def _save_manifest(self) -> None:
        """Save manifest to disk."""
        self.manifest_file.write_text(json.dumps(self.manifest, indent=2, default=str))
    
    def _calculate_checksum(self, filepath: Path) -> str:
        """Calculate MD5 checksum for a file."""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _get_backup_name(self, backup_type: str = 'full') -> str:
        """Generate backup filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"backup_{backup_type}_{timestamp}.zip"
    
    def create_backup(self, backup_type: str = 'full', 
                      compress: bool = True) -> Dict:
        """
        Create a backup of the source directory.
        
        Args:
            backup_type: 'full' or 'incremental'
            compress: Whether to compress the backup
            
        Returns:
            Backup information dictionary
        """
        print(f"\n📦 Creating {backup_type} backup...")
        print(f"   Source: {self.source_dir}")
        print(f"   Destination: {self.backup_dir}")
        
        backup_name = self._get_backup_name(backup_type)
        backup_path = self.backup_dir / backup_name
        
        files_backed_up = []
        total_size = 0
        
        if compress:
            # Create compressed backup
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in self.source_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.source_dir)
                        zipf.write(file_path, arcname)
                        files_backed_up.append(str(arcname))
                        total_size += file_path.stat().st_size
        else:
            # Create uncompressed backup (copy directory)
            backup_path = self.backup_dir / backup_name.replace('.zip', '')
            shutil.copytree(self.source_dir, backup_path)
            for file_path in backup_path.rglob('*'):
                if file_path.is_file():
                    files_backed_up.append(str(file_path.relative_to(backup_path)))
                    total_size += file_path.stat().st_size
        
        # Calculate checksum
        checksum = self._calculate_checksum(backup_path) if backup_path.is_file() else None
        
        # Create backup info
        backup_info = {
            'name': backup_name,
            'path': str(backup_path),
            'type': backup_type,
            'compressed': compress,
            'created_at': datetime.now().isoformat(),
            'source_dir': str(self.source_dir),
            'file_count': len(files_backed_up),
            'original_size': total_size,
            'backup_size': backup_path.stat().st_size if backup_path.exists() else 0,
            'checksum': checksum,
            'files': files_backed_up
        }
        
        # Update manifest
        self.manifest['backups'].append(backup_info)
        self._save_manifest()
        
        # Apply rotation
        self._rotate_backups()
        
        print(f"\n✅ Backup created successfully!")
        print(f"   Files: {len(files_backed_up)}")
        print(f"   Original size: {total_size / 1024:.2f} KB")
        print(f"   Backup size: {backup_info['backup_size'] / 1024:.2f} KB")
        if checksum:
            print(f"   Checksum: {checksum[:16]}...")
        
        return backup_info
    
    def _rotate_backups(self) -> None:
        """Remove old backups beyond the maximum limit."""
        max_backups = self.manifest['settings'].get('max_backups', 5)
        
        while len(self.manifest['backups']) > max_backups:
            oldest = self.manifest['backups'].pop(0)
            old_path = Path(oldest['path'])
            if old_path.exists():
                if old_path.is_file():
                    old_path.unlink()
                else:
                    shutil.rmtree(old_path)
                print(f"🗑️ Rotated out old backup: {oldest['name']}")
        
        self._save_manifest()
    
    def restore_backup(self, backup_name: str = None, 
                       restore_dir: str = None) -> bool:
        """
        Restore from a backup.
        
        Args:
            backup_name: Name of backup to restore (default: latest)
            restore_dir: Directory to restore to (default: source_dir)
            
        Returns:
            True if successful
        """
        # Find backup
        if backup_name:
            backup_info = next(
                (b for b in self.manifest['backups'] if b['name'] == backup_name),
                None
            )
        else:
            backup_info = self.manifest['backups'][-1] if self.manifest['backups'] else None
        
        if not backup_info:
            print("❌ No backup found to restore!")
            return False
        
        backup_path = Path(backup_info['path'])
        if not backup_path.exists():
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        restore_path = Path(restore_dir) if restore_dir else self.source_dir
        
        print(f"\n🔄 Restoring backup: {backup_info['name']}")
        print(f"   To: {restore_path}")
        
        # Verify checksum
        if backup_info.get('checksum'):
            current_checksum = self._calculate_checksum(backup_path)
            if current_checksum != backup_info['checksum']:
                print("⚠️ Warning: Checksum mismatch! Backup may be corrupted.")
        
        # Restore
        if backup_info['compressed']:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(restore_path)
        else:
            shutil.copytree(backup_path, restore_path, dirs_exist_ok=True)
        
        print(f"✅ Restored {backup_info['file_count']} files!")
        return True
    
    def list_backups(self) -> List[Dict]:
        """List all available backups."""
        print("\n📋 Available Backups:")
        print("=" * 60)
        
        for i, backup in enumerate(self.manifest['backups'], 1):
            status = "✅" if Path(backup['path']).exists() else "❌"
            print(f"{i}. {status} {backup['name']}")
            print(f"   Created: {backup['created_at']}")
            print(f"   Files: {backup['file_count']} | Size: {backup['backup_size']/1024:.1f} KB")
            print()
        
        if not self.manifest['backups']:
            print("   No backups found.")
        
        return self.manifest['backups']
    
    def verify_backup(self, backup_name: str) -> bool:
        """Verify backup integrity."""
        backup_info = next(
            (b for b in self.manifest['backups'] if b['name'] == backup_name),
            None
        )
        
        if not backup_info:
            print(f"❌ Backup not found: {backup_name}")
            return False
        
        backup_path = Path(backup_info['path'])
        if not backup_path.exists():
            print(f"❌ Backup file missing!")
            return False
        
        if backup_info.get('checksum'):
            current_checksum = self._calculate_checksum(backup_path)
            if current_checksum == backup_info['checksum']:
                print(f"✅ Backup verified: {backup_name}")
                return True
            else:
                print(f"❌ Checksum mismatch! Backup may be corrupted.")
                return False
        
        print(f"⚠️ No checksum available for verification.")
        return True
    
    def set_max_backups(self, max_count: int) -> None:
        """Set maximum number of backups to retain."""
        self.manifest['settings']['max_backups'] = max_count
        self._save_manifest()
        print(f"📝 Max backups set to: {max_count}")


# Demo usage
if __name__ == "__main__":
    import tempfile
    
    print("💾 Backup Manager Demo")
    print("=" * 50)
    
    # Create demo source directory with files
    with tempfile.TemporaryDirectory() as source_temp:
        with tempfile.TemporaryDirectory() as backup_temp:
            # Create sample files
            source_dir = Path(source_temp)
            for i in range(5):
                (source_dir / f"document_{i}.txt").write_text(f"Document content {i}")
            (source_dir / "data").mkdir()
            (source_dir / "data" / "records.csv").write_text("id,name\n1,John\n2,Jane")
            
            print(f"\n📁 Created sample source directory with files")
            
            # Initialize backup manager
            manager = BackupManager(source_temp, backup_temp)
            manager.set_max_backups(3)
            
            # Create multiple backups
            print("\n" + "=" * 50)
            manager.create_backup(backup_type='full', compress=True)
            
            # Add a new file
            (source_dir / "new_file.txt").write_text("New content")
            manager.create_backup(backup_type='full', compress=True)
            
            # List backups
            manager.list_backups()
            
            print("\n🎉 Backup Manager Demo Complete!")
