#!/usr/bin/env python3
"""
Traffic Visualization Module
Creates charts and graphs for traffic analysis results
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
import statistics

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False


class TrafficVisualizer:
    """Creates visualizations for traffic analysis results"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.plotting_available = PLOTTING_AVAILABLE
        
        if self.plotting_available:
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
    
    def create_summary_charts(self, analysis_result: Dict) -> List[str]:
        """Create summary charts from analysis results"""
        if not self.plotting_available:
            return ["Visualization libraries not available. Install matplotlib and seaborn."]
        
        chart_files = []
        
        # Traffic overview chart
        overview_file = self._create_traffic_overview_chart(analysis_result)
        if overview_file:
            chart_files.append(overview_file)
        
        # Bot detection results
        bot_chart_file = self._create_bot_detection_chart(analysis_result)
        if bot_chart_file:
            chart_files.append(bot_chart_file)
        
        # Top threats visualization
        threats_file = self._create_threats_chart(analysis_result)
        if threats_file:
            chart_files.append(threats_file)
        
        return chart_files
    
    def _create_traffic_overview_chart(self, analysis_result: Dict) -> Optional[str]:
        """Create traffic overview pie chart"""
        try:
            summary = analysis_result.get('traffic_summary', {})
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Traffic Analysis Overview', fontsize=16, fontweight='bold')
            
            # Status codes pie chart
            status_codes = summary.get('status_codes', {})
            if status_codes:
                ax1.pie(status_codes.values(), labels=status_codes.keys(), autopct='%1.1f%%')
                ax1.set_title('HTTP Status Codes Distribution')
            
            # Methods bar chart
            methods = summary.get('methods', {})
            if methods:
                ax2.bar(methods.keys(), methods.values())
                ax2.set_title('HTTP Methods')
                ax2.set_ylabel('Request Count')
            
            # Countries distribution
            countries = summary.get('top_countries', {})
            if countries:
                countries_subset = dict(list(countries.items())[:10])  # Top 10
                ax3.barh(list(countries_subset.keys()), list(countries_subset.values()))
                ax3.set_title('Top Countries')
                ax3.set_xlabel('Request Count')
            
            # Bot vs Legitimate traffic
            total_requests = summary.get('total_requests', 0)
            bot_requests = int(total_requests * summary.get('bot_request_rate', 0))
            legitimate_requests = total_requests - bot_requests
            
            ax4.pie([legitimate_requests, bot_requests], 
                   labels=['Legitimate', 'Bot Traffic'], 
                   autopct='%1.1f%%',
                   colors=['lightgreen', 'lightcoral'])
            ax4.set_title('Traffic Composition')
            
            plt.tight_layout()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/traffic_overview_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filename
            
        except Exception as e:
            print(f"Error creating traffic overview chart: {e}")
            return None
    
    def _create_bot_detection_chart(self, analysis_result: Dict) -> Optional[str]:
        """Create bot detection results chart"""
        try:
            bot_analysis = analysis_result.get('bot_analysis', {})
            summary = bot_analysis.get('summary', {})
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            fig.suptitle('Bot Detection Results', fontsize=16, fontweight='bold')
            
            # Risk level distribution
            risk_dist = summary.get('risk_distribution', {})
            if risk_dist:
                colors = {'CRITICAL': 'red', 'HIGH': 'orange', 'MEDIUM': 'yellow', 'LOW': 'green'}
                bar_colors = [colors.get(level, 'gray') for level in risk_dist.keys()]
                
                ax1.bar(risk_dist.keys(), risk_dist.values(), color=bar_colors)
                ax1.set_title('Risk Level Distribution')
                ax1.set_ylabel('Number of IPs')
                ax1.tick_params(axis='x', rotation=45)
            
            # Bot percentage gauge
            bot_percentage = summary.get('bot_percentage', 0)
            
            # Create a simple gauge using pie chart
            sizes = [bot_percentage, 100 - bot_percentage]
            colors = ['lightcoral', 'lightgray']
            
            wedges, texts, autotexts = ax2.pie(sizes, colors=colors, startangle=90, 
                                              counterclock=False, autopct='%1.1f%%')
            
            # Create hole in center for gauge effect
            centre_circle = plt.Circle((0,0), 0.50, fc='white')
            ax2.add_artist(centre_circle)
            ax2.set_title('Bot Traffic Percentage')
            
            plt.tight_layout()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/bot_detection_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filename
            
        except Exception as e:
            print(f"Error creating bot detection chart: {e}")
            return None
    
    def _create_threats_chart(self, analysis_result: Dict) -> Optional[str]:
        """Create top threats visualization"""
        try:
            threats = analysis_result.get('top_threats', [])
            if not threats:
                return None
            
            # Limit to top 10 threats
            top_threats = threats[:10]
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            fig.suptitle('Top Security Threats', fontsize=16, fontweight='bold')
            
            # Threat scores bar chart
            ips = [threat['ip'] for threat in top_threats]
            scores = [threat['threat_score'] for threat in top_threats]
            risk_levels = [threat['risk_level'] for threat in top_threats]
            
            # Color code by risk level
            color_map = {'CRITICAL': 'red', 'HIGH': 'orange', 'MEDIUM': 'yellow', 'LOW': 'green'}
            colors = [color_map.get(level, 'gray') for level in risk_levels]
            
            bars = ax1.barh(ips, scores, color=colors)
            ax1.set_title('Threat Scores by IP Address')
            ax1.set_xlabel('Threat Score')
            
            # Add score labels on bars
            for bar, score in zip(bars, scores):
                ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                        f'{score}', va='center')
            
            # Request rates scatter plot
            request_rates = [threat['requests_per_minute'] for threat in top_threats]
            error_rates = [threat['error_rate'] * 100 for threat in top_threats]  # Convert to percentage
            
            scatter = ax2.scatter(request_rates, error_rates, c=scores, cmap='Reds', s=100, alpha=0.7)
            ax2.set_xlabel('Requests per Minute')
            ax2.set_ylabel('Error Rate (%)')
            ax2.set_title('Request Rate vs Error Rate (Color = Threat Score)')
            
            # Add colorbar
            plt.colorbar(scatter, ax=ax2, label='Threat Score')
            
            plt.tight_layout()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/top_threats_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filename
            
        except Exception as e:
            print(f"Error creating threats chart: {e}")
            return None
    
    def generate_html_report(self, analysis_result: Dict, chart_files: List[str]) -> str:
        """Generate HTML report with embedded charts"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = f"{self.output_dir}/report_{timestamp}.html"
        
        # Extract key metrics
        summary = analysis_result.get('traffic_summary', {})
        bot_summary = analysis_result.get('bot_analysis', {}).get('summary', {})
        threats = analysis_result.get('top_threats', [])[:5]  # Top 5
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bot Traffic Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .metric-card {{ background: white; border: 1px solid #ddd; border-radius: 8px; 
                       padding: 15px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #666; font-size: 0.9em; }}
        .threat-item {{ padding: 10px; margin: 5px 0; border-radius: 5px; }}
        .critical {{ background-color: #ffebee; border-left: 4px solid #f44336; }}
        .high {{ background-color: #fff3e0; border-left: 4px solid #ff9800; }}
        .medium {{ background-color: #f3e5f5; border-left: 4px solid #9c27b0; }}
        .low {{ background-color: #e8f5e8; border-left: 4px solid #4caf50; }}
        .chart {{ text-align: center; margin: 20px 0; }}
        .chart img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 8px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Bot Traffic Analysis Report</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Log File: {analysis_result.get('metadata', {}).get('log_file', 'N/A')}</p>
    </div>

    <div class="metric-card">
        <h2>📊 Key Metrics</h2>
        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
            <div>
                <div class="metric-value">{summary.get('total_requests', 0):,}</div>
                <div class="metric-label">Total Requests</div>
            </div>
            <div>
                <div class="metric-value">{summary.get('unique_ips', 0):,}</div>
                <div class="metric-label">Unique IPs</div>
            </div>
            <div>
                <div class="metric-value">{bot_summary.get('detected_bots', 0)}</div>
                <div class="metric-label">Detected Bots</div>
            </div>
            <div>
                <div class="metric-value">{bot_summary.get('bot_percentage', 0):.1f}%</div>
                <div class="metric-label">Bot Percentage</div>
            </div>
            <div>
                <div class="metric-value">{summary.get('error_rate', 0) * 100:.1f}%</div>
                <div class="metric-label">Error Rate</div>
            </div>
            <div>
                <div class="metric-value">{summary.get('requests_per_hour', 0):.0f}</div>
                <div class="metric-label">Requests/Hour</div>
            </div>
        </div>
    </div>
"""
        
        # Add charts if available
        if chart_files:
            html_content += """
    <div class="metric-card">
        <h2>📈 Visual Analysis</h2>
"""
            for chart_file in chart_files:
                chart_name = chart_file.split('/')[-1].replace('_', ' ').replace('.png', '').title()
                html_content += f"""
        <div class="chart">
            <h3>{chart_name}</h3>
            <img src="{chart_file.split('/')[-1]}" alt="{chart_name}">
        </div>
"""
            html_content += "    </div>\n"
        
        # Add top threats
        if threats:
            html_content += """
    <div class="metric-card">
        <h2>🚨 Top Threats</h2>
"""
            for i, threat in enumerate(threats, 1):
                risk_class = threat['risk_level'].lower()
                html_content += f"""
        <div class="threat-item {risk_class}">
            <strong>#{i}. {threat['ip']}</strong> ({threat['risk_level']} Risk)<br>
            <small>Score: {threat['threat_score']} | Requests: {threat['request_count']} | 
            Rate: {threat['requests_per_minute']:.1f}/min | Error Rate: {threat['error_rate']:.1%}</small><br>
            <small><strong>Action:</strong> {threat['recommended_action']}</small>
        </div>
"""
            html_content += "    </div>\n"
        
        # Add recommendations
        recommendations = analysis_result.get('recommendations', {})
        immediate_actions = recommendations.get('immediate_actions', [])
        
        if immediate_actions:
            html_content += """
    <div class="metric-card">
        <h2>💡 Immediate Recommendations</h2>
        <ul>
"""
            for action in immediate_actions:
                html_content += f"""
            <li><strong>{action['action']}</strong> ({action['priority']})<br>
                <small>{action['details']}</small></li>
"""
            html_content += """
        </ul>
    </div>
"""
        
        html_content += """
    <div class="metric-card">
        <h2>📋 Summary</h2>
        <p>This report provides a comprehensive analysis of your web traffic, identifying potential bot activity and security threats. 
        The analysis uses multiple detection methods including request rate analysis, user agent fingerprinting, and behavioral pattern recognition.</p>
        
        <p><strong>Next Steps:</strong></p>
        <ul>
            <li>Review and implement the recommended immediate actions</li>
            <li>Monitor the identified IP addresses for continued suspicious activity</li>
            <li>Consider implementing the suggested rate limiting and blocking measures</li>
            <li>Schedule regular analysis to maintain security posture</li>
        </ul>
    </div>

    <footer style="text-align: center; margin-top: 40px; color: #666; font-size: 0.9em;">
        <p>Generated by Bot Traffic Analyzer v1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </footer>
</body>
</html>
"""
        
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_filename
