"""
Bot Traffic Analyzer Configuration
Core settings and thresholds for the bot detection system
"""

# Detection Thresholds
RATE_LIMITS = {
    'requests_per_minute': 10,
    'requests_per_hour': 300,
    'error_rate_threshold': 0.3,
    'suspicious_path_threshold': 0.1,
    'bot_confidence_threshold': 0.5
}

# DDoS Detection Settings
DDOS_DETECTION = {
    'time_window_minutes': 5,
    'min_requests_threshold': 1000,
    'min_ip_diversity': 0.1,
    'min_error_rate': 0.5
}

# Bot Signatures and Patterns
BOT_SIGNATURES = {
    'user_agent_patterns': [
        r'curl/.*', r'wget/.*', r'python-requests/.*',
        r'Go-http-client/.*', r'.*bot.*', r'.*crawler.*',
        r'.*spider.*', r'.*scraper.*', r'HTTPie/.*', r'axios/.*'
    ],
    'suspicious_paths': [
        '/.env', '/admin', '/wp-admin', '/phpmyadmin', '/config',
        '/backup', '/database', '/xmlrpc.php', '/wp-config.php',
        '/server-status', '/server-info', '/.git', '/.svn',
        '/api/v1/admin', '/api/admin', '/administrator'
    ]
}

# Risk Level Calculations
RISK_SCORING = {
    'request_rate_weight': 0.3,
    'user_agent_weight': 0.3,
    'path_diversity_weight': 0.2,
    'error_rate_weight': 0.2,
    'suspicious_paths_weight': 0.4,
    'timing_pattern_weight': 0.1,
    'risk_thresholds': {
        'critical': 0.9, 'high': 0.7, 'medium': 0.5, 'low': 0.0
    }
}

# Output Settings
OUTPUT_CONFIG = {
    'max_top_threats': 10,
    'max_sample_entries': 5,
    'include_detailed_patterns': True,
    'generate_blocklists': True,
    'blocklist_min_risk': 'high'
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/bot_analyzer.log'
}
