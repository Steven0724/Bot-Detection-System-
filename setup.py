#!/usr/bin/env python3
"""
Setup and Quick Start Script for Bot Traffic Analyzer
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Requirements installed successfully")
            return True
        else:
            print(f"❌ Failed to install requirements: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing requirements: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    directories = ["output", "logs"]
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"📁 Created directory: {dir_name}")


def run_sample_analysis():
    """Run analysis on sample log file"""
    print("\n🧪 Running sample analysis...")
    
    if not Path("sample_logs.txt").exists():
        print("❌ Sample log file not found")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, "src/main_analyzer.py", "sample_logs.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Sample analysis completed successfully")
            print("\n📊 Sample Output:")
            print(result.stdout[-500:])  # Show last 500 characters
            return True
        else:
            print(f"❌ Analysis failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Bot Traffic Analyzer Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install requirements
    if not install_requirements():
        print("\n⚠️  Manual installation required:")
        print("   pip install pandas numpy python-dateutil")
        print("   (Other packages are optional)")
    
    # Run sample analysis
    if Path("sample_logs.txt").exists():
        run_sample_analysis()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\n📚 Quick Start Commands:")
    print("   # Analyze your log file:")
    print("   python src/main_analyzer.py your_log_file.log")
    print("\n   # Run with Docker:")
    print("   docker build -t bot-analyzer .")
    print("   docker run -v $(pwd)/logs:/app/logs -v $(pwd)/output:/app/output bot-analyzer /app/logs/your_log.log")
    print("\n   # Run system test:")
    print("   python test_system.py")
    print("\n📁 Results will be saved in the 'output' directory")


if __name__ == "__main__":
    main()
