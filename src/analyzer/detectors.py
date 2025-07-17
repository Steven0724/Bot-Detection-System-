import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass
import statistics

from src.analyzer.core import LogEntry, TrafficPattern


@dataclass
class BotSignature:
    """Represents a bot detection signature"""
    name: str
    user_agent_patterns: List[str]
    behavior_patterns: List[str]
    confidence_score: float
    description: str = ""


@dataclass
class BotDetectionResult:
    """Result of bot detection analysis"""
    ip: str
    is_bot: bool
    confidence: float
    reasons: List[str]
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    recommended_action: str


class BotDetector:
    """Advanced bot detection using multiple signals"""
    
    def __init__(self):
        self.bot_signatures = self._load_bot_signatures()
        self.suspicious_patterns = self._load_suspicious_patterns()
        self.rate_limit_thresholds = {
            'requests_per_minute': 10,
            'requests_per_hour': 300,
            'error_rate_threshold': 0.3,
            'suspicious_path_threshold': 0.1
        }
    
    def _load_bot_signatures(self) -> List[BotSignature]:
        """Load known bot signatures"""
        signatures = [
            BotSignature(
                name="Curl Bot",
                user_agent_patterns=[r"curl/.*"],
                behavior_patterns=["high_frequency", "single_path", "tool_based"],
                confidence_score=0.9,
                description="Command-line tool often used for automated requests"
            ),
            BotSignature(
                name="Python Requests",
                user_agent_patterns=[r"python-requests/.*"],
                behavior_patterns=["high_frequency", "api_focused", "automated"],
                confidence_score=0.8,
                description="Python HTTP library commonly used in scripts"
            ),
            BotSignature(
                name="Wget Bot",
                user_agent_patterns=[r"Wget/.*"],
                behavior_patterns=["sequential_download", "high_frequency"],
                confidence_score=0.9,
                description="Download tool often used for scraping"
            ),
            BotSignature(
                name="Generic Bot",
                user_agent_patterns=[r".*bot.*", r".*crawler.*", r".*spider.*"],
                behavior_patterns=["systematic_crawling"],
                confidence_score=0.7,
                description="Generic bot patterns in user agent"
            ),
            BotSignature(
                name="Headless Browser",
                user_agent_patterns=[r"HeadlessChrome.*", r"PhantomJS.*"],
                behavior_patterns=["automated_browsing"],
                confidence_score=0.6,
                description="Headless browser automation"
            ),
            BotSignature(
                name="Security Scanner",
                user_agent_patterns=[r".*scan.*", r".*vuln.*", r".*security.*"],
                behavior_patterns=["vulnerability_scanning", "path_enumeration"],
                confidence_score=0.95,
                description="Security scanning tools"
            )
        ]
        return signatures
    
    def _load_suspicious_patterns(self) -> Dict[str, List[str]]:
        """Load suspicious behavior patterns"""
        return {
            'malicious_paths': [
                '/.env', '/admin', '/wp-admin', '/phpmyadmin', '/config',
                '/backup', '/database', '/xmlrpc.php', '/wp-config.php',
                '/server-status', '/server-info', '/.git', '/.svn',
                '/api/v1/admin', '/api/admin', '/administrator'
            ],
            'vulnerability_paths': [
                '/etc/passwd', '/proc/version', '/windows/system32',
                '/../../../', '/cgi-bin/', '/shell.php', '/upload.php'
            ],
            'bot_behaviors': [
                'rapid_sequential_requests',
                'identical_intervals',
                'no_referrer_headers',
                'single_session_high_volume',
                'error_code_farming'
            ]
        }
    
    def detect_bots(self, traffic_patterns: Dict[str, TrafficPattern]) -> Dict[str, BotDetectionResult]:
        """Detect bots from traffic patterns"""
        results = {}
        
        for ip, pattern in traffic_patterns.items():
            detection_result = self._analyze_single_ip(pattern)
            results[ip] = detection_result
        
        return results
    
    def _analyze_single_ip(self, pattern: TrafficPattern) -> BotDetectionResult:
        """Analyze a single IP for bot behavior"""
        confidence = 0.0
        reasons = []
        
        # Rate-based detection
        if pattern.requests_per_minute > self.rate_limit_thresholds['requests_per_minute']:
            confidence += 0.3
            reasons.append(f"High request rate: {pattern.requests_per_minute:.1f} req/min")
        
        # User agent analysis
        bot_ua_score = self._analyze_user_agents(pattern.user_agents)
        confidence += bot_ua_score * 0.3
        if bot_ua_score > 0:
            reasons.append("Bot-like user agent detected")
        
        # Path diversity analysis
        if pattern.unique_paths == 1 and pattern.request_count > 10:
            confidence += 0.2
            reasons.append("Low path diversity with high volume")
        
        # Error rate analysis
        if pattern.error_rate > self.rate_limit_thresholds['error_rate_threshold']:
            confidence += 0.2
            reasons.append(f"High error rate: {pattern.error_rate:.1%}")
        
        # Suspicious path analysis
        if pattern.suspicious_requests > 0:
            confidence += 0.4
            reasons.append(f"Suspicious path requests: {pattern.suspicious_requests}")
        
        # Response time analysis (bots often have consistent timing)
        if self._is_timing_suspicious(pattern):
            confidence += 0.1
            reasons.append("Suspicious timing patterns")
        
        # Determine final classification
        is_bot = confidence > 0.5
        risk_level = self._calculate_risk_level(confidence, pattern)
        recommended_action = self._recommend_action(risk_level, pattern)
        
        return BotDetectionResult(
            ip=pattern.ip,
            is_bot=is_bot,
            confidence=min(1.0, confidence),
            reasons=reasons,
            risk_level=risk_level,
            recommended_action=recommended_action
        )
    
    def _analyze_user_agents(self, user_agents: List[str]) -> float:
        """Analyze user agents for bot indicators"""
        if not user_agents:
            return 0.5  # No user agent is suspicious
        
        bot_score = 0.0
        for ua in user_agents:
            for signature in self.bot_signatures:
                for pattern in signature.user_agent_patterns:
                    if re.match(pattern, ua, re.IGNORECASE):
                        bot_score = max(bot_score, signature.confidence_score)
        
        return bot_score
    
    def _is_timing_suspicious(self, pattern: TrafficPattern) -> bool:
        """Check if timing patterns suggest bot behavior"""
        # This would require access to individual request timings
        # For now, we'll use a simplified heuristic
        return (pattern.requests_per_minute > 5 and 
                pattern.avg_response_time < 100)  # Very fast responses
    
    def _calculate_risk_level(self, confidence: float, pattern: TrafficPattern) -> str:
        """Calculate risk level based on confidence and impact"""
        if confidence >= 0.9 or pattern.suspicious_requests > 5:
            return "CRITICAL"
        elif confidence >= 0.7 or pattern.requests_per_minute > 20:
            return "HIGH"
        elif confidence >= 0.5 or pattern.requests_per_minute > 10:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _recommend_action(self, risk_level: str, pattern: TrafficPattern) -> str:
        """Recommend action based on risk level"""
        actions = {
            "CRITICAL": "BLOCK_IMMEDIATELY - High confidence malicious bot",
            "HIGH": "RATE_LIMIT_STRICT - Apply strict rate limiting",
            "MEDIUM": "RATE_LIMIT_MODERATE - Apply moderate rate limiting", 
            "LOW": "MONITOR - Continue monitoring for patterns"
        }
        return actions.get(risk_level, "MONITOR")
    
    def generate_bot_report(self, detection_results: Dict[str, BotDetectionResult]) -> Dict:
        """Generate comprehensive bot detection report"""
        total_ips = len(detection_results)
        bot_ips = [result for result in detection_results.values() if result.is_bot]
        
        risk_distribution = Counter(result.risk_level for result in detection_results.values())
        
        # Top bot IPs by confidence
        top_bots = sorted(
            [result for result in detection_results.values() if result.is_bot],
            key=lambda x: x.confidence,
            reverse=True
        )[:10]
        
        # Recommended actions summary
        action_summary = Counter(result.recommended_action.split(' - ')[0] 
                               for result in detection_results.values())
        
        return {
            'summary': {
                'total_ips_analyzed': total_ips,
                'detected_bots': len(bot_ips),
                'bot_percentage': len(bot_ips) / total_ips * 100 if total_ips > 0 else 0,
                'risk_distribution': dict(risk_distribution)
            },
            'top_bots': [
                {
                    'ip': bot.ip,
                    'confidence': bot.confidence,
                    'risk_level': bot.risk_level,
                    'reasons': bot.reasons[:3]  # Top 3 reasons
                } for bot in top_bots
            ],
            'recommended_actions': dict(action_summary),
            'immediate_blocks': [
                result.ip for result in detection_results.values() 
                if result.risk_level == "CRITICAL"
            ],
            'rate_limit_candidates': [
                result.ip for result in detection_results.values() 
                if result.risk_level in ["HIGH", "MEDIUM"]
            ]
        }
    
    def export_blocklist(self, detection_results: Dict[str, BotDetectionResult], 
                        min_risk_level: str = "HIGH") -> List[str]:
        """Export list of IPs to block"""
        risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        min_level = risk_order[min_risk_level]
        
        return [
            result.ip for result in detection_results.values()
            if risk_order[result.risk_level] >= min_level
        ]
