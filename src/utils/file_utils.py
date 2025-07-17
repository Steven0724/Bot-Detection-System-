#!/usr/bin/env python3
"""
File Utilities
Helper functions for file operations and management
"""

import os
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FileUtils:
    """Utility class for file operations"""
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> Path:
        """Ensure a directory exists, create if it doesn't"""
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    @staticmethod
    def get_file_line_count(file_path: str) -> int:
        """Get number of lines in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
    
    @staticmethod
    def read_file_sample(file_path: str, num_lines: int = 10) -> List[str]:
        """Read first N lines of a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return [next(f, '').strip() for _ in range(num_lines)]
        except Exception:
            return []
    
    @staticmethod
    def save_json(data: Any, file_path: str, indent: int = 2) -> bool:
        """Save data as JSON file"""
        try:
            FileUtils.ensure_directory_exists(os.path.dirname(file_path))
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, default=str, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving JSON to {file_path}: {e}")
            return False
    
    @staticmethod
    def load_json(file_path: str) -> Optional[Dict[str, Any]]:
        """Load data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON from {file_path}: {e}")
            return None
    
    @staticmethod
    def save_text_list(data: List[str], file_path: str) -> bool:
        """Save list of strings to text file (one per line)"""
        try:
            FileUtils.ensure_directory_exists(os.path.dirname(file_path))
            with open(file_path, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(f"{item}\n")
            return True
        except Exception as e:
            logger.error(f"Error saving text list to {file_path}: {e}")
            return False
    
    @staticmethod
    def load_text_list(file_path: str) -> List[str]:
        """Load list of strings from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Error loading text list from {file_path}: {e}")
            return []
    
    @staticmethod
    def save_csv(data: List[Dict[str, Any]], file_path: str) -> bool:
        """Save list of dictionaries as CSV"""
        try:
            if not data:
                return False
            
            FileUtils.ensure_directory_exists(os.path.dirname(file_path))
            fieldnames = data[0].keys()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            logger.error(f"Error saving CSV to {file_path}: {e}")
            return False
    
    @staticmethod
    def get_timestamped_filename(base_name: str, extension: str = "", 
                                directory: str = "") -> str:
        """Generate timestamped filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if extension and not extension.startswith('.'):
            extension = f".{extension}"
        
        filename = f"{base_name}_{timestamp}{extension}"
        
        if directory:
            return os.path.join(directory, filename)
        return filename
    
    @staticmethod
    def find_log_files(directory: str, patterns: List[str] = None) -> List[str]:
        """Find log files in directory matching patterns"""
        if patterns is None:
            patterns = ['*.log', '*.txt', 'access*', 'error*']
        
        log_files = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            return log_files
        
        for pattern in patterns:
            log_files.extend(directory_path.glob(pattern))
        
        return [str(f) for f in log_files if f.is_file()]
    
    @staticmethod
    def backup_file(file_path: str, backup_suffix: str = ".bak") -> str:
        """Create backup of a file"""
        backup_path = f"{file_path}{backup_suffix}"
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            logger.error(f"Error creating backup of {file_path}: {e}")
            return ""
    
    @staticmethod
    def cleanup_old_files(directory: str, days_old: int = 7, 
                         pattern: str = "*") -> int:
        """Remove files older than specified days"""
        removed_count = 0
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
        
        try:
            for file_path in Path(directory).glob(pattern):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    removed_count += 1
                    logger.info(f"Removed old file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
        
        return removed_count
    
    @staticmethod
    def get_disk_usage(directory: str) -> Dict[str, int]:
        """Get disk usage statistics for directory"""
        try:
            import shutil
            usage = shutil.disk_usage(directory)
            return {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free
            }
        except Exception:
            return {'total': 0, 'used': 0, 'free': 0}
    
    @staticmethod
    def compress_file(file_path: str, compression: str = 'gzip') -> str:
        """Compress a file using specified compression"""
        try:
            if compression == 'gzip':
                import gzip
                compressed_path = f"{file_path}.gz"
                with open(file_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        f_out.writelines(f_in)
                return compressed_path
            else:
                logger.error(f"Unsupported compression type: {compression}")
                return ""
        except Exception as e:
            logger.error(f"Error compressing file {file_path}: {e}")
            return ""
