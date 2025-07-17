"""
Configuration file for Bot Traffic Analyzer
Customize detection thresholds and behavior patterns
"""

# Detection Thresholds
RATE_LIMITS = {
    # Requests per minute threshold for bot detection
    'requests_per_minute': 10,
    
    # Requests per hour threshold for rate limiting
    'requests_per_hour': 300,
    
    # Error rate threshold (0.0 - 1.0)
    'error_rate_threshold': 0.3,
    
    # Percentage of suspicious path requests (0.0 - 1.0)
    'suspicious_path_threshold': 0.1,
    
    # Bot confidence threshold for classification (0.0 - 1.0)
    'bot_confidence_threshold': 0.5
}

# DDoS Detection Settings
DDOS_DETECTION = {
    # Time window for DDoS analysis (minutes)
    'time_window_minutes': 5,
    
    # Minimum requests in window to trigger alert
    'min_requests_threshold': 1000,
    
    # Minimum unique IP diversity percentage
    'min_ip_diversity': 0.1,
    
    # Minimum error rate for DDoS classification
    'min_error_rate': 0.5
}

# Known Bot Patterns
BOT_SIGNATURES = {
    'user_agent_patterns': [
        r'curl/.*',
        r'wget/.*',
        r'python-requests/.*',
        r'Go-http-client/.*',
        r'.*bot.*',
        r'.*crawler.*',
        r'.*spider.*',
        r'.*scraper.*',
        r'HTTPie/.*',
        r'axios/.*'
    ],
    
    'suspicious_paths': [
        '/.env',
        '/admin',
        '/wp-admin',
        '/phpmyadmin',
        '/config',
        '/backup',
        '/database',
        '/xmlrpc.php',
        '/wp-config.php',
        '/server-status',
        '/server-info',
        '/.git',
        '/.svn',
        '/api/v1/admin',
        '/api/admin',
        '/administrator',
        '/etc/passwd',
        '/proc/version',
        '/windows/system32',
        '/../../../',
        '/cgi-bin/',
        '/shell.php',
        '/upload.php'
    ]
}

# Risk Level Calculations
RISK_SCORING = {
    # Score weights for different factors
    'request_rate_weight': 0.3,
    'user_agent_weight': 0.3,
    'path_diversity_weight': 0.2,
    'error_rate_weight': 0.2,
    'suspicious_paths_weight': 0.4,
    'timing_pattern_weight': 0.1,
    
    # Risk level thresholds
    'risk_thresholds': {
        'critical': 0.9,
        'high': 0.7,
        'medium': 0.5,
        'low': 0.0
    }
}

# Recommended Actions
ACTIONS = {
    'critical': 'BLOCK_IMMEDIATELY',
    'high': 'RATE_LIMIT_STRICT',
    'medium': 'RATE_LIMIT_MODERATE',
    'low': 'MONITOR'
}

# Cost-Effective Solutions
SOLUTIONS = {
    'free_tier': [
        {
            'name': 'Nginx Rate Limiting',
            'cost': 'FREE',
            'description': 'Use nginx limit_req module for basic rate limiting',
            'effectiveness': 'HIGH',
            'implementation': 'Add limit_req_zone to nginx.conf'
        },
        {
            'name': 'Fail2ban Integration',
            'cost': 'FREE', 
            'description': 'Automatic IP blocking based on suspicious patterns',
            'effectiveness': 'MEDIUM',
            'implementation': 'Configure fail2ban with custom filters'
        },
        {
            'name': 'Cloudflare Free Tier',
            'cost': 'FREE',
            'description': 'Basic DDoS protection and bot management',
            'effectiveness': 'HIGH',
            'implementation': 'Change DNS to Cloudflare'
        },
        {
            'name': 'Linux iptables',
            'cost': 'FREE',
            'description': 'Firewall-level IP blocking',
            'effectiveness': 'HIGH',
            'implementation': 'Add iptables rules for blocking IPs'
        }
    ],
    
    'low_cost': [
        {
            'name': 'Cloudflare Pro',
            'cost': '$20/month',
            'description': 'Advanced bot management and analytics',
            'effectiveness': 'VERY_HIGH',
            'implementation': 'Upgrade to Cloudflare Pro plan'
        },
        {
            'name': 'AWS WAF',
            'cost': '$5-50/month',
            'description': 'Web Application Firewall with bot detection',
            'effectiveness': 'HIGH',
            'implementation': 'Configure AWS WAF with bot control rules'
        }
    ]
}

# Output Settings
OUTPUT_CONFIG = {
    # Maximum number of top threats to include in reports
    'max_top_threats': 10,
    
    # Maximum number of sample log entries to include
    'max_sample_entries': 5,
    
    # Include detailed pattern analysis in output
    'include_detailed_patterns': True,
    
    # Generate blocklist files
    'generate_blocklists': True,
    
    # Minimum risk level for blocklist inclusion
    'blocklist_min_risk': 'high'
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'bot_analyzer.log'
}
