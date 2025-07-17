#!/usr/bin/env python3
"""
Log Parser Module
Parses different log formats and extracts relevant information
"""

import re
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass

from src.analyzer.core import LogEntry


class LogParser:
    """Parser for web server access logs"""
    
    def __init__(self):
        self.patterns = {
            'common': self._get_common_log_pattern(),
            'combined': self._get_combined_log_pattern(),
            'custom': self._get_custom_log_pattern()
        }
    
    def _get_common_log_pattern(self) -> str:
        """Common Log Format pattern"""
        return r'^(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) ([^"]*) \S+" (\d+) (\d+|-)'
    
    def _get_combined_log_pattern(self) -> str:
        """Combined Log Format pattern"""
        return r'^(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) ([^"]*) \S+" (\d+) (\d+|-) "([^"]*)" "([^"]*)"'
    
    def _get_custom_log_pattern(self) -> str:
        """Custom log format pattern based on the provided example"""
        # Pattern for: IP - COUNTRY - [TIMESTAMP] "METHOD PATH HTTP/1.1" STATUS SIZE "REFERER" "USER_AGENT" RESPONSE_TIME
        return r'^(\S+) - (\S+) - \[([^\]]+)\] "(\S+) ([^"]*) HTTP/[\d\.]+"\s+(\d+)\s+(\d+)\s+"([^"]*)"\s+"([^"]*)"\s+(\d+)$'
    
    def parse_log_line(self, line: str) -> Optional[LogEntry]:
        """
        Parse a single log line and return a LogEntry object
        
        Args:
            line: Raw log line string
            
        Returns:
            LogEntry object or None if parsing fails
        """
        line = line.strip()
        if not line or line.startswith('#'):
            return None
        
        # Try custom format first (based on the example)
        entry = self._parse_custom_format(line)
        if entry:
            return entry
        
        # Try combined format
        entry = self._parse_combined_format(line)
        if entry:
            return entry
        
        # Try common format
        entry = self._parse_common_format(line)
        if entry:
            return entry
        
        return None
    
    def _parse_custom_format(self, line: str) -> Optional[LogEntry]:
        """Parse custom log format"""
        match = re.match(self.patterns['custom'], line)
        if not match:
            return None
        
        try:
            ip = match.group(1)
            country = match.group(2)
            timestamp_str = match.group(3)
            method = match.group(4)
            path = match.group(5)
            status_code = int(match.group(6))
            response_size = int(match.group(7)) if match.group(7) != '-' else 0
            referer = match.group(8)
            user_agent = match.group(9)
            response_time = int(match.group(10))
            
            # Parse timestamp
            timestamp = self._parse_timestamp(timestamp_str)
            if not timestamp:
                return None
            
            return LogEntry(
                ip=ip,
                country=country,
                timestamp=timestamp,
                method=method,
                path=path,
                status_code=status_code,
                response_size=response_size,
                user_agent=user_agent,
                response_time=response_time
            )
        
        except (ValueError, IndexError) as e:
            return None
    
    def _parse_combined_format(self, line: str) -> Optional[LogEntry]:
        """Parse combined log format"""
        match = re.match(self.patterns['combined'], line)
        if not match:
            return None
        
        try:
            ip = match.group(1)
            timestamp_str = match.group(2)
            method = match.group(3)
            path = match.group(4)
            status_code = int(match.group(5))
            response_size = int(match.group(6)) if match.group(6) != '-' else 0
            referer = match.group(7)
            user_agent = match.group(8)
            
            # Parse timestamp
            timestamp = self._parse_timestamp(timestamp_str)
            if not timestamp:
                return None
            
            return LogEntry(
                ip=ip,
                country='--',  # Not available in combined format
                timestamp=timestamp,
                method=method,
                path=path,
                status_code=status_code,
                response_size=response_size,
                user_agent=user_agent,
                response_time=0  # Not available in combined format
            )
        
        except (ValueError, IndexError) as e:
            return None
    
    def _parse_common_format(self, line: str) -> Optional[LogEntry]:
        """Parse common log format"""
        match = re.match(self.patterns['common'], line)
        if not match:
            return None
        
        try:
            ip = match.group(1)
            timestamp_str = match.group(2)
            method = match.group(3)
            path = match.group(4)
            status_code = int(match.group(5))
            response_size = int(match.group(6)) if match.group(6) != '-' else 0
            
            # Parse timestamp
            timestamp = self._parse_timestamp(timestamp_str)
            if not timestamp:
                return None
            
            return LogEntry(
                ip=ip,
                country='--',  # Not available in common format
                timestamp=timestamp,
                method=method,
                path=path,
                status_code=status_code,
                response_size=response_size,
                user_agent='',  # Not available in common format
                response_time=0  # Not available in common format
            )
        
        except (ValueError, IndexError) as e:
            return None
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object"""
        # Common timestamp formats
        formats = [
            '%d/%b/%Y:%H:%M:%S %z',  # Apache format with timezone
            '%d/%b/%Y:%H:%M:%S',     # Apache format without timezone
            '%d/%m/%Y:%H:%M:%S',     # Alternative date format
            '%Y-%m-%d %H:%M:%S',     # ISO-like format
            '%d/%b/%Y:%H:%M:%S +0000', # With explicit timezone
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # Try to handle timezone manually if needed
        if '+' in timestamp_str or '-' in timestamp_str:
            # Remove timezone for basic parsing
            timestamp_clean = re.sub(r'[+-]\d{4}$', '', timestamp_str).strip()
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_clean, fmt)
                except ValueError:
                    continue
        
        return None
    
    def parse_log_file(self, file_path: str) -> List[LogEntry]:
        """
        Parse entire log file and return list of LogEntry objects
        
        Args:
            file_path: Path to log file
            
        Returns:
            List of LogEntry objects
        """
        entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                for line_num, line in enumerate(file, 1):
                    entry = self.parse_log_line(line)
                    if entry:
                        entries.append(entry)
                    elif line.strip() and not line.startswith('#'):
                        # Log parsing failures for debugging
                        pass
                        
        except Exception as e:
            raise Exception(f"Failed to parse log file {file_path}: {str(e)}")
        
        return entries
    
    def validate_log_format(self, file_path: str, sample_size: int = 100) -> Dict:
        """
        Validate log format and return statistics
        
        Args:
            file_path: Path to log file
            sample_size: Number of lines to sample for validation
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'total_lines': 0,
            'parsed_lines': 0,
            'failed_lines': 0,
            'detected_format': None,
            'sample_failures': []
        }
        
        format_matches = {'custom': 0, 'combined': 0, 'common': 0}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                for line_num, line in enumerate(file, 1):
                    results['total_lines'] += 1
                    
                    if line_num <= sample_size:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        # Test each format
                        if re.match(self.patterns['custom'], line):
                            format_matches['custom'] += 1
                            results['parsed_lines'] += 1
                        elif re.match(self.patterns['combined'], line):
                            format_matches['combined'] += 1
                            results['parsed_lines'] += 1
                        elif re.match(self.patterns['common'], line):
                            format_matches['common'] += 1
                            results['parsed_lines'] += 1
                        else:
                            results['failed_lines'] += 1
                            if len(results['sample_failures']) < 5:
                                results['sample_failures'].append(f"Line {line_num}: {line[:100]}...")
                    
                    if line_num >= sample_size:
                        break
        
        except Exception as e:
            results['error'] = str(e)
            return results
        
        # Determine most likely format
        if format_matches:
            results['detected_format'] = max(format_matches, key=format_matches.get)
            results['format_confidence'] = format_matches[results['detected_format']] / max(1, sum(format_matches.values()))
        
        return results
    
    def get_log_statistics(self, file_path: str) -> Dict:
        """
        Get basic statistics about the log file
        
        Args:
            file_path: Path to log file
            
        Returns:
            Dictionary with log statistics
        """
        stats = {
            'total_lines': 0,
            'file_size': 0,
            'date_range': None,
            'unique_ips': set(),
            'status_codes': {},
            'methods': {},
            'sample_entries': []
        }
        
        try:
            import os
            stats['file_size'] = os.path.getsize(file_path)
            
            entries = self.parse_log_file(file_path)
            stats['total_lines'] = len(entries)
            
            if entries:
                # Date range
                timestamps = [entry.timestamp for entry in entries]
                stats['date_range'] = {
                    'start': min(timestamps),
                    'end': max(timestamps)
                }
                
                # Unique IPs
                stats['unique_ips'] = len(set(entry.ip for entry in entries))
                
                # Status codes
                from collections import Counter
                stats['status_codes'] = dict(Counter(entry.status_code for entry in entries))
                
                # Methods
                stats['methods'] = dict(Counter(entry.method for entry in entries))
                
                # Sample entries
                stats['sample_entries'] = entries[:5]
        
        except Exception as e:
            stats['error'] = str(e)
        
        return stats