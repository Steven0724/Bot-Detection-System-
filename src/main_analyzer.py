#!/usr/bin/env python3
"""
Main Traffic Analyzer Entry Point
"""

import sys
import os
import argparse
import json
import re
import glob
import shutil
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(__file__))

@dataclass
class LogEntry:
    ip: str
    country: str
    timestamp: datetime
    method: str
    path: str
    status_code: int
    response_size: int
    user_agent: str
    response_time: int
    
    @property
    def is_bot_user_agent(self):
        bot_indicators = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python-requests']
        return any(indicator in self.user_agent.lower() for indicator in bot_indicators)
    
    @property
    def is_suspicious_path(self):
        suspicious_paths = ['/.env', '/admin', '/wp-admin', '/phpmyadmin', '/config']
        return any(sus_path in self.path for sus_path in suspicious_paths)

def cleanup_all_output():
    """Aggressively remove ALL old analysis files"""
    output_dirs = ['output', 'test_output']
    
    for output_dir in output_dirs:
        if not os.path.exists(output_dir):
            continue
            
        print(f"🧹 Cleaning {output_dir}/ directory...")
        
        # Remove ALL files with analysis patterns including PNG
        patterns = [
            '*.png',                    # ALL PNG files
            '*.csv',                    # ALL CSV files  
            '*.json',                   # ALL JSON files
            '*.txt',                    # ALL TXT files
            'traffic_dashboard_*.png',
            'traffic_analysis_*.csv', 
            'traffic_report_*.json',
            'blocklist_*.txt',
            'summary_*.txt',
            'analysis_*.txt',
            'bot_report_*.txt'
        ]
        
        files_removed = 0
        for pattern in patterns:
            files = glob.glob(os.path.join(output_dir, pattern))
            for old_file in files:
                try:
                    os.remove(old_file)
                    files_removed += 1
                except OSError:
                    pass
        
        # Remove chart directories
        chart_dirs = glob.glob(os.path.join(output_dir, 'charts_*'))
        for old_dir in chart_dirs:
            try:
                import shutil
                shutil.rmtree(old_dir)
                files_removed += 1
            except OSError:
                pass
        
        if files_removed > 0:
            print(f"   ✅ Removed {files_removed} old files from {output_dir}/")

def parse_log_line(line):
    """Parse a single log line"""
    pattern = r'(\S+) - (\S+) - \[([^\]]+)\] "(\S+) ([^"]+)" (\d+) (\d+) "[^"]*" "([^"]*)" (\d+)'
    match = re.match(pattern, line.strip())
    
    if not match:
        return None
    
    ip, country, timestamp_str, method, path_and_protocol, status_code, response_size, user_agent, response_time = match.groups()
    
    # Extract path from "GET /path HTTP/1.1"
    path = path_and_protocol.split(' ')[0]
    
    # Parse timestamp - FIX FOR YOUR FORMAT
    try:
        # Your format: 01/07/2025:06:00:01
        timestamp = datetime.strptime(timestamp_str, '%d/%m/%Y:%H:%M:%S')
    except ValueError:
        try:
            # Fallback: 01/Jul/2025:06:00:01
            timestamp = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S')
        except ValueError:
            return None
    
    return LogEntry(
        ip=ip,
        country=country,
        timestamp=timestamp,
        method=method,
        path=path,
        status_code=int(status_code),
        response_size=int(response_size),
        user_agent=user_agent,
        response_time=int(response_time)
    )

def save_analysis_reports(analysis_results, output_dir="output"):
    """Save analysis results in multiple formats"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON report
    json_file = os.path.join(output_dir, f'traffic_analysis_{timestamp}.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    # Save text summary
    summary_file = os.path.join(output_dir, f'summary_{timestamp}.txt')
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("TRAFFIC ANALYSIS SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Analysis Time: {datetime.now().isoformat()}\n")
        f.write(f"Total Requests: {analysis_results['total_requests']:,}\n")
        f.write(f"Unique IPs: {analysis_results['unique_ips']:,}\n")
        f.write(f"Bot Requests: {analysis_results['bot_requests']:,}\n")
        f.write(f"Bot Percentage: {analysis_results['bot_percentage']:.1f}%\n\n")
        
        f.write("TOP THREATS\n")
        f.write("-" * 40 + "\n")
        for i, threat in enumerate(analysis_results['top_threats'][:10], 1):
            f.write(f"{i}. {threat['ip']} ({threat['risk_level']}) - {threat['request_count']} requests\n")
    
    # Save CSV report
    csv_file = os.path.join(output_dir, f'traffic_analysis_{timestamp}.csv')
    try:
        import csv
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['IP', 'Risk_Level', 'Confidence', 'Requests', 'Bot_Activity', 'Suspicious_Activity'])
            
            for threat in analysis_results['top_threats']:
                writer.writerow([
                    threat['ip'],
                    threat['risk_level'],
                    f"{threat['confidence_score']:.1f}%",
                    threat['request_count'],
                    'Yes' if threat.get('bot_activity', 0) > 0 else 'No',
                    'Yes' if threat.get('suspicious_activity', 0) > 0 else 'No'
                ])
    except Exception as e:
        print(f"Warning: Could not save CSV: {e}")
    
    print(f"\n📁 REPORTS GENERATED:")
    print(f"   📄 JSON Report: {json_file}")
    print(f"   📋 Summary: {summary_file}")
    print(f"   📊 CSV Data: {csv_file}")
    
    return {
        'json': json_file,
        'summary': summary_file,
        'csv': csv_file
    }

def main():
    """Main entry point for the traffic analyzer"""
    parser = argparse.ArgumentParser(description='Professional Traffic Analyzer')
    parser.add_argument('log_file', help='Path to the log file to analyze')
    parser.add_argument('--format', choices=['json', 'txt'], default='txt', help='Output format')
    parser.add_argument('--keep-old', action='store_true', help='Keep old analysis files')
    
    args = parser.parse_args()
    
    # FORCE cleanup unless --keep-old flag is used
    if not args.keep_old:
        print("🧹 Starting aggressive cleanup...")
        cleanup_all_output()
        print("✅ Cleanup completed")
    
    # Check if log file exists
    log_file_path = Path(args.log_file)
    if not log_file_path.exists():
        print(f"❌ Error: Log file '{args.log_file}' not found")
        return 1
    
    print(f"📁 Processing: {log_file_path}")
    print(f"📊 File size: {log_file_path.stat().st_size:,} bytes")
    
    # Parse log file
    log_entries = []
    total_lines = 0
    
    print("🔍 Parsing log file...")
    with open(log_file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            total_lines = line_num
            if line.strip():
                entry = parse_log_line(line)
                if entry:
                    log_entries.append(entry)
            
            if line_num % 1000 == 0:
                print(f"  Processed {line_num} lines, parsed {len(log_entries)} entries...")
    
    print(f"✅ Successfully parsed {len(log_entries):,} entries from {total_lines:,} lines")
    
    if not log_entries:
        print("❌ No valid log entries found")
        return 1
    
    # Analyze data
    print("🧠 Analyzing traffic patterns...")
    
    total_requests = len(log_entries)
    unique_ips = len(set(entry.ip for entry in log_entries))
    bot_requests = sum(1 for entry in log_entries if entry.is_bot_user_agent or entry.is_suspicious_path)
    human_requests = total_requests - bot_requests
    bot_percentage = (bot_requests / total_requests) * 100 if total_requests > 0 else 0
    
    # IP analysis
    ip_counts = {}
    for entry in log_entries:
        ip = entry.ip
        if ip not in ip_counts:
            ip_counts[ip] = {
                'count': 0,
                'user_agents': set(),
                'paths': set(),
                'bot_activity': 0,
                'suspicious_activity': 0
            }
        
        ip_counts[ip]['count'] += 1
        ip_counts[ip]['user_agents'].add(entry.user_agent)
        ip_counts[ip]['paths'].add(entry.path)
        
        if entry.is_bot_user_agent:
            ip_counts[ip]['bot_activity'] += 1
        if entry.is_suspicious_path:
            ip_counts[ip]['suspicious_activity'] += 1
    
    # Calculate risk levels
    ip_analysis = []
    for ip, data in ip_counts.items():
        confidence = 0
        risk_level = 'LOW'
        
        # High request count
        if data['count'] > 100:
            confidence += 30
            risk_level = 'HIGH'
        elif data['count'] > 50:
            confidence += 20
            risk_level = 'MEDIUM'
        
        # Bot activity
        if data['bot_activity'] > 0:
            confidence += 40
            risk_level = 'HIGH'
        
        # Suspicious activity
        if data['suspicious_activity'] > 0:
            confidence += 40
            risk_level = 'CRITICAL'
        
        confidence = min(confidence, 100)
        
        ip_analysis.append({
            'ip': ip,
            'request_count': data['count'],
            'risk_level': risk_level,
            'confidence_score': confidence,
            'bot_activity': data['bot_activity'],
            'suspicious_activity': data['suspicious_activity']
        })
    
    # Sort by risk and confidence
    ip_analysis.sort(key=lambda x: (
        {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}.get(x['risk_level'], 0),
        x['confidence_score']
    ), reverse=True)
    
    # Prepare analysis results for saving
    analysis_results = {
        'total_requests': total_requests,
        'unique_ips': unique_ips,
        'bot_requests': bot_requests,
        'human_requests': human_requests,
        'bot_percentage': bot_percentage,
        'top_threats': ip_analysis,
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    # Save reports
    print("💾 Generating reports...")
    reports = save_analysis_reports(analysis_results)
    
    # Generate professional 4-in-1 dashboard
    print("📊 Creating professional dashboard...")
    try:
        from analyzer.professional_visualizer import ProfessionalVisualizer
        
        # Prepare data for visualization
        viz_data = {
            'log_entries': []
        }
        
        # Convert log entries to dict format for visualizer
        for entry in log_entries:
            viz_data['log_entries'].append({
                'timestamp': entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'ip': entry.ip,
                'method': entry.method,
                'status_code': entry.status_code,
                'user_agent': entry.user_agent,
                'path': entry.path,
                'response_size': entry.response_size
            })
        
        # Summary data for pie chart
        summary_data = {
            'unique_ips': unique_ips,
            'detected_bots': len([ip for ip in ip_analysis if ip['risk_level'] in ['HIGH', 'CRITICAL']]),
            'total_requests': total_requests
        }
        
        # Generate the dashboard
        visualizer = ProfessionalVisualizer('output')
        dashboard_reports = visualizer.generate_professional_reports(viz_data, summary_data)
        
        print(f"✅ Professional reports generated:")
        print(f"   📊 Dashboard (PNG): {dashboard_reports['dashboard']}")
        print(f"   📄 JSON Report: {dashboard_reports['json']}")
        print(f"   📋 CSV Data: {dashboard_reports['csv']}")
        print(f"   📝 TXT Summary: {dashboard_reports['summary']}")
        
    except ImportError:
        print("⚠️  Professional visualizer not available")
    except Exception as e:
        print(f"⚠️  Dashboard generation failed: {e}")
    
    # Display results
    print("\n" + "="*80)
    print("🛡️  PROFESSIONAL TRAFFIC ANALYSIS & BOT DETECTION REPORT  🛡️")
    print("="*80)
    
    print("\n📊 TRAFFIC ANALYSIS SUMMARY")
    print("-" * 50)
    print(f"📈 Total Requests: {total_requests:,}")
    print(f"🌐 Unique IP Addresses: {unique_ips:,}")
    print(f"🤖 Bot Requests Detected: {bot_requests:,} ({bot_percentage:.1f}%)")
    print(f"👥 Human Traffic: {human_requests:,} ({100-bot_percentage:.1f}%)")
    
    # Show only suspicious IPs
    suspicious_ips = [ip for ip in ip_analysis if ip['risk_level'] in ['MEDIUM', 'HIGH', 'CRITICAL']]
    
    if suspicious_ips:
        print("\n🚨 SECURITY THREAT ANALYSIS")
        print("-" * 50)
        threats_found = 0
        
        print(f"{'IP Address':<15} | {'Risk Level':<12} | {'Confidence':<12} | {'Requests':<10}")
        print("-" * 65)
        
        for ip_data in suspicious_ips[:10]:
            ip = ip_data['ip']
            risk = ip_data['risk_level']
            confidence = ip_data['confidence_score']
            request_count = ip_data['request_count']
            
            if risk == 'CRITICAL':
                risk_display = f"🔴 {risk}"
                threats_found += 1
            elif risk == 'HIGH':
                risk_display = f"🟠 {risk}"
                threats_found += 1
            elif risk == 'MEDIUM':
                risk_display = f"🟡 {risk}"
            
            print(f"{ip:<15} | {risk_display:<20} | {confidence:>6.1f}%     | {request_count:>8,}")
        
        if threats_found > 0:
            print(f"\n⚠️  CRITICAL ALERT: {threats_found} HIGH-RISK THREATS DETECTED!")
        else:
            print(f"\n⚠️  {len(suspicious_ips)} MEDIUM-RISK THREATS DETECTED - MONITOR CLOSELY")
    else:
        print("\n✅ NO SUSPICIOUS ACTIVITY DETECTED")
        print("-" * 50)
        print("All analyzed IPs show normal traffic patterns")
    
    # Security recommendations
    print(f"\n💡 SECURITY RECOMMENDATIONS")
    print("-" * 50)
    
    if bot_percentage > 50:
        print("  🔴 IMMEDIATE ACTION REQUIRED:")
        print("     • Block high-risk IPs immediately")
        print("     • Implement rate limiting")
        print("     • Review firewall rules")
    elif bot_percentage > 20:
        print("  🟡 MODERATE RISK:")
        print("     • Monitor suspicious IPs closely")
        print("     • Consider implementing CAPTCHA")
        print("     • Enhance logging")
    else:
        print("  🟢 LOW RISK:")
        print("     • Continue regular monitoring")
        print("     • Review logs periodically")
    
    print(f"\n" + "="*80)
    print(f"✅ Analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
if __name__ == "__main__":
    sys.exit(main())
