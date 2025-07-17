#!/usr/bin/env python3
"""
Analysis Result Model
Data model for storing complete analysis results
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json


@dataclass
class ThreatInfo:
    """Information about a detected threat"""
    ip: str
    threat_score: float
    risk_level: str
    confidence: float
    request_count: int
    requests_per_minute: float
    suspicious_requests: int
    error_rate: float
    reasons: List[str]
    recommended_action: str
    country: Optional[str] = None
    user_agents: List[str] = field(default_factory=list)


@dataclass
class TrafficSummary:
    """Summary of overall traffic statistics"""
    total_requests: int
    unique_ips: int
    error_rate: float
    bot_request_rate: float
    suspicious_request_rate: float
    requests_per_hour: float
    time_span_hours: float
    status_codes: Dict[str, int]
    top_countries: Dict[str, int]
    methods: Dict[str, int]
    top_paths: Dict[str, int]
    date_range: Dict[str, datetime]


@dataclass
class BotAnalysisSummary:
    """Summary of bot detection results"""
    total_ips_analyzed: int
    detected_bots: int
    bot_percentage: float
    risk_distribution: Dict[str, int]
    immediate_blocks: List[str]
    rate_limit_candidates: List[str]
    recommended_actions: Dict[str, int]


@dataclass
class DDosAlert:
    """Information about a potential DDoS attack"""
    timestamp: datetime
    request_count: int
    unique_ips: int
    error_rate: float
    severity: str
    top_ips: Dict[str, int]
    duration_minutes: int = 5


@dataclass
class RecommendationAction:
    """A recommended action to take"""
    priority: str
    action: str
    details: str
    implementation: str
    cost: str = "FREE"
    effectiveness: str = "MEDIUM"


@dataclass
class AnalysisMetadata:
    """Metadata about the analysis run"""
    log_file: str
    analysis_timestamp: datetime
    total_entries: int
    analysis_version: str
    processing_time_seconds: float = 0.0
    analyzer_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Complete analysis result containing all findings and recommendations"""
    metadata: AnalysisMetadata
    traffic_summary: TrafficSummary
    bot_analysis: BotAnalysisSummary
    top_threats: List[ThreatInfo]
    ddos_alerts: List[DDosAlert]
    recommendations: Dict[str, List[RecommendationAction]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        def convert_dataclass(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {field.name: convert_dataclass(getattr(obj, field.name)) 
                       for field in obj.__dataclass_fields__.values()}
            elif isinstance(obj, list):
                return [convert_dataclass(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: convert_dataclass(value) for key, value in obj.items()}
            elif isinstance(obj, datetime):
                return obj.isoformat()
            else:
                return obj
        
        return convert_dataclass(self)
    
    def to_json(self, filepath: str = None) -> str:
        """Convert to JSON string or save to file"""
        json_data = json.dumps(self.to_dict(), indent=2, default=str)
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_data)
        
        return json_data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """Create AnalysisResult from dictionary"""
        # This would need more complex deserialization logic
        # For now, we'll keep it simple and just use the dict data
        return cls(**data)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get key summary statistics"""
        return {
            'total_requests': self.traffic_summary.total_requests,
            'unique_ips': self.traffic_summary.unique_ips,
            'detected_bots': self.bot_analysis.detected_bots,
            'bot_percentage': self.bot_analysis.bot_percentage,
            'critical_threats': len([t for t in self.top_threats if t.risk_level == 'CRITICAL']),
            'high_threats': len([t for t in self.top_threats if t.risk_level == 'HIGH']),
            'ddos_alerts': len(self.ddos_alerts),
            'immediate_actions_needed': len(self.recommendations.get('immediate_actions', [])),
            'processing_time': self.metadata.processing_time_seconds
        }
    
    def get_blocking_recommendations(self) -> Dict[str, List[str]]:
        """Get IP blocking recommendations by risk level"""
        recommendations = {
            'immediate_block': [],
            'rate_limit_strict': [],
            'rate_limit_moderate': [],
            'monitor_only': []
        }
        
        for threat in self.top_threats:
            if threat.risk_level == 'CRITICAL':
                recommendations['immediate_block'].append(threat.ip)
            elif threat.risk_level == 'HIGH':
                recommendations['rate_limit_strict'].append(threat.ip)
            elif threat.risk_level == 'MEDIUM':
                recommendations['rate_limit_moderate'].append(threat.ip)
            else:
                recommendations['monitor_only'].append(threat.ip)
        
        return recommendations
    
    def export_blocklist(self, risk_levels: List[str] = None) -> List[str]:
        """Export IP addresses for blocking based on risk levels"""
        if risk_levels is None:
            risk_levels = ['CRITICAL', 'HIGH']
        
        blocklist = []
        for threat in self.top_threats:
            if threat.risk_level in risk_levels:
                blocklist.append(threat.ip)
        
        return list(set(blocklist))  # Remove duplicates
    
    def generate_executive_summary(self) -> str:
        """Generate a brief executive summary"""
        stats = self.get_summary_stats()
        
        summary = f"""
EXECUTIVE SUMMARY - Bot Traffic Analysis

Analysis Period: {self.metadata.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Log File: {self.metadata.log_file}

KEY FINDINGS:
• Total Requests Analyzed: {stats['total_requests']:,}
• Unique IP Addresses: {stats['unique_ips']:,}
• Bot Traffic Detected: {stats['detected_bots']} IPs ({stats['bot_percentage']:.1f}%)
• Critical Threats: {stats['critical_threats']}
• High-Risk Threats: {stats['high_threats']}

IMMEDIATE ACTIONS REQUIRED: {stats['immediate_actions_needed']}
DDoS ALERTS: {stats['ddos_alerts']}

RECOMMENDATION:
"""
        
        if stats['critical_threats'] > 0:
            summary += f"IMMEDIATE ACTION REQUIRED - Block {stats['critical_threats']} critical threat IP(s)\n"
        elif stats['high_threats'] > 0:
            summary += f"HIGH PRIORITY - Implement rate limiting for {stats['high_threats']} suspicious IP(s)\n"
        elif stats['detected_bots'] > 0:
            summary += "MODERATE CONCERN - Monitor detected bot activity\n"
        else:
            summary += "LOW RISK - No significant threats detected\n"
        
        return summary.strip()
