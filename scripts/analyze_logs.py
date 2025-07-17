#!/usr/bin/env python3
"""
Log Analysis Script
Analyzes web server logs for bot traffic and security threats
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.main_analyzer import TrafficAnalysisOrchestrator


def main():
    """Main entry point for log analysis"""
    parser = argparse.ArgumentParser(
        description='Analyze web server logs for bot traffic and security threats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_logs.py access.log
  python analyze_logs.py /var/log/nginx/access.log --output-dir reports
  python analyze_logs.py *.log --batch --quiet

For more information, see README.md and USAGE_GUIDE.md
        """
    )
    
    parser.add_argument('log_files', nargs='+', help='Log file(s) to analyze')
    parser.add_argument('--output-dir', default='output', help='Output directory for results')
    parser.add_argument('--batch', action='store_true', help='Batch mode for multiple files')
    parser.add_argument('--quiet', action='store_true', help='Suppress progress output')
    parser.add_argument('--format', choices=['json', 'html', 'both'], default='both',
                       help='Output format')
    parser.add_argument('--min-risk', choices=['low', 'medium', 'high', 'critical'], 
                       default='medium', help='Minimum risk level for reporting')
    
    args = parser.parse_args()
    
    orchestrator = TrafficAnalysisOrchestrator(args.output_dir)
    
    for log_file in args.log_files:
        if not Path(log_file).exists():
            print(f"❌ Log file not found: {log_file}")
            continue
        
        try:
            if not args.quiet:
                print(f"🔍 Analyzing: {log_file}")
            
            analysis_result = orchestrator.analyze_log_file(log_file)
            
            if 'error' in analysis_result:
                print(f"❌ Analysis failed for {log_file}: {analysis_result['error']}")
                continue
            
            # Save results
            report_file = orchestrator.save_results(analysis_result, f"analysis_{Path(log_file).stem}")
            
            if not args.quiet:
                summary = analysis_result['bot_analysis']['summary']
                print(f"✅ Analysis complete: {summary['detected_bots']} bots detected")
                print(f"📁 Results: {report_file}")
                
        except Exception as e:
            print(f"❌ Error analyzing {log_file}: {e}")
            if not args.quiet:
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()
