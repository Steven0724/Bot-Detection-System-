#!/usr/bin/env python3
"""
Validation Utilities
Data validation and sanitization functions
"""

import re
import ipaddress
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ValidationUtils:
    """Utility class for data validation"""
    
    @staticmethod
    def is_valid_ip(ip_str: str) -> bool:
        """Validate if string is a valid IP address"""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_private_ip(ip_str: str) -> bool:
        """Check if IP address is in private range"""
        try:
            ip = ipaddress.ip_address(ip_str)
            return ip.is_private
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_http_method(method: str) -> bool:
        """Validate HTTP method"""
        valid_methods = {
            'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 
            'PATCH', 'TRACE', 'CONNECT'
        }
        return method.upper() in valid_methods
    
    @staticmethod
    def is_valid_status_code(status_code: int) -> bool:
        """Validate HTTP status code"""
        return 100 <= status_code <= 599
    
    @staticmethod
    def sanitize_user_agent(user_agent: str) -> str:
        """Sanitize user agent string"""
        if not user_agent or user_agent == '-':
            return 'Unknown'
        
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>"\']', '', user_agent)
        
        # Truncate if too long
        if len(sanitized) > 500:
            sanitized = sanitized[:500] + '...'
        
        return sanitized.strip()
    
    @staticmethod
    def validate_log_entry_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate log entry data completeness and correctness"""
        errors = []
        
        # Required fields
        required_fields = ['ip', 'timestamp', 'method', 'path', 'status_code']
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate IP address
        if 'ip' in data and not ValidationUtils.is_valid_ip(data['ip']):
            errors.append(f"Invalid IP address: {data.get('ip')}")
        
        # Validate HTTP method
        if 'method' in data and not ValidationUtils.is_valid_http_method(data['method']):
            errors.append(f"Invalid HTTP method: {data.get('method')}")
        
        # Validate status code
        if 'status_code' in data:
            try:
                status = int(data['status_code'])
                if not ValidationUtils.is_valid_status_code(status):
                    errors.append(f"Invalid status code: {status}")
            except (ValueError, TypeError):
                errors.append(f"Status code must be integer: {data.get('status_code')}")
        
        # Validate timestamp
        if 'timestamp' in data and not isinstance(data['timestamp'], datetime):
            errors.append("Timestamp must be datetime object")
        
        # Validate response size
        if 'response_size' in data and data['response_size'] is not None:
            try:
                size = int(data['response_size'])
                if size < 0:
                    errors.append("Response size cannot be negative")
            except (ValueError, TypeError):
                errors.append(f"Response size must be integer: {data.get('response_size')}")
        
        # Validate response time
        if 'response_time' in data and data['response_time'] is not None:
            try:
                time = int(data['response_time'])
                if time < 0:
                    errors.append("Response time cannot be negative")
            except (ValueError, TypeError):
                errors.append(f"Response time must be integer: {data.get('response_time')}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize URL path for analysis"""
        if not path:
            return '/'
        
        # Remove query parameters and fragments
        path = path.split('?')[0].split('#')[0]
        
        # Ensure starts with /
        if not path.startswith('/'):
            path = '/' + path
        
        # Remove double slashes
        path = re.sub(r'/+', '/', path)
        
        # Decode URL encoding
        try:
            import urllib.parse
            path = urllib.parse.unquote(path)
        except Exception:
            pass
        
        return path.lower()  # Case insensitive
    
    @staticmethod
    def extract_country_code(country_str: str) -> str:
        """Extract and validate country code"""
        if not country_str or country_str in ['-', '--', 'Unknown']:
            return 'XX'  # Unknown country
        
        # Clean the string
        country = country_str.strip().upper()
        
        # Validate length (should be 2 characters for ISO codes)
        if len(country) == 2 and country.isalpha():
            return country
        
        # Map common variations
        country_mappings = {
            'UNITED STATES': 'US',
            'UNITED KINGDOM': 'GB', 
            'GREAT BRITAIN': 'GB',
            'CANADA': 'CA',
            'AUSTRALIA': 'AU',
            'GERMANY': 'DE',
            'FRANCE': 'FR',
            'JAPAN': 'JP',
            'CHINA': 'CN',
            'RUSSIA': 'RU'
        }
        
        return country_mappings.get(country, 'XX')
    
    @staticmethod
    def validate_analysis_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate analysis configuration"""
        errors = []
        
        # Validate rate limits
        if 'rate_limits' in config:
            rate_config = config['rate_limits']
            
            if 'requests_per_minute' in rate_config:
                rpm = rate_config['requests_per_minute']
                if not isinstance(rpm, (int, float)) or rpm <= 0:
                    errors.append("requests_per_minute must be positive number")
            
            if 'error_rate_threshold' in rate_config:
                err_rate = rate_config['error_rate_threshold']
                if not isinstance(err_rate, (int, float)) or not 0 <= err_rate <= 1:
                    errors.append("error_rate_threshold must be between 0 and 1")
        
        # Validate DDoS settings
        if 'ddos_detection' in config:
            ddos_config = config['ddos_detection']
            
            if 'time_window_minutes' in ddos_config:
                window = ddos_config['time_window_minutes']
                if not isinstance(window, int) or window <= 0:
                    errors.append("time_window_minutes must be positive integer")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file operations"""
        if not filename:
            return 'unnamed'
        
        # Remove path separators and special characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
        
        # Trim and remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Ensure not empty
        if not sanitized:
            sanitized = 'unnamed'
        
        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        
        return sanitized
    
    @staticmethod
    def validate_file_path(file_path: str) -> Tuple[bool, str]:
        """Validate file path for security and accessibility"""
        import os
        
        try:
            # Check if path exists
            if not os.path.exists(file_path):
                return False, f"File does not exist: {file_path}"
            
            # Check if it's a file (not directory)
            if not os.path.isfile(file_path):
                return False, f"Path is not a file: {file_path}"
            
            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                return False, f"File is not readable: {file_path}"
            
            # Check file size (warn if too large)
            file_size = os.path.getsize(file_path)
            if file_size > 1024 * 1024 * 1024:  # 1GB
                return True, f"Warning: Large file ({file_size / 1024 / 1024:.1f} MB)"
            
            return True, "Valid file path"
            
        except Exception as e:
            return False, f"Error validating file path: {str(e)}"
    
    @staticmethod
    def detect_log_format(sample_lines: List[str]) -> Optional[str]:
        """Detect log format from sample lines"""
        if not sample_lines:
            return None
        
        # Patterns for different log formats
        patterns = {
            'apache_common': r'^\S+ \S+ \S+ \[[^\]]+\] "\S+ [^"]* \S+" \d+ \d+',
            'apache_combined': r'^\S+ \S+ \S+ \[[^\]]+\] "\S+ [^"]* \S+" \d+ \d+ "[^"]*" "[^"]*"',
            'nginx_combined': r'^\S+ - \S+ \[[^\]]+\] "\S+ [^"]* \S+" \d+ \d+ "[^"]*" "[^"]*"',
            'custom': r'^\S+ - \S+ - \[[^\]]+\] "\S+ [^"]* HTTP/[\d\.]+"\s+\d+\s+\d+\s+"[^"]*"\s+"[^"]*"\s+\d+$'
        }
        
        format_scores = {fmt: 0 for fmt in patterns}
        
        for line in sample_lines[:10]:  # Check first 10 lines
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            for fmt, pattern in patterns.items():
                if re.match(pattern, line):
                    format_scores[fmt] += 1
        
        # Return format with highest score
        if max(format_scores.values()) > 0:
            return max(format_scores, key=format_scores.get)
        
        return None
