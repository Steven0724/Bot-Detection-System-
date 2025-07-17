#!/usr/bin/env python3
"""
Report Generation Script
Generates comprehensive reports from analysis results
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.analyzer.visualizations import TrafficVisualizer


def main():
    """Generate reports from analysis results"""
    parser = argparse.ArgumentParser(description='Generate reports from bot analysis results')
    parser.add_argument('analysis_file', help='Analysis result JSON file')
    parser.add_argument('--output-dir', default='reports', help='Output directory for reports')
    parser.add_argument('--format', choices=['html', 'pdf', 'charts'], default='html',
                       help='Report format')
    parser.add_argument('--include-charts', action='store_true', help='Include visualization charts')
    
    args = parser.parse_args()
    
    # Load analysis results
    try:
        with open(args.analysis_file, 'r', encoding='utf-8') as f:
            analysis_result = json.load(f)
    except Exception as e:
        print(f"❌ Error loading analysis file: {e}")
        return 1
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Initialize visualizer
    visualizer = TrafficVisualizer(str(output_dir))
    
    try:
        if args.format == 'html' or args.include_charts:
            print("📊 Generating charts...")
            chart_files = visualizer.create_summary_charts(analysis_result)
            
            print("📄 Generating HTML report...")
            html_file = visualizer.generate_html_report(analysis_result, chart_files)
            print(f"✅ HTML report generated: {html_file}")
        
        if args.format == 'charts':
            print("📊 Generating charts only...")
            chart_files = visualizer.create_summary_charts(analysis_result)
            print(f"✅ Generated {len(chart_files)} chart files")
            for chart in chart_files:
                print(f"   📈 {chart}")
                
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
