# Installation Guide

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 512MB available memory
- **Storage**: 100MB free disk space
- **Network**: Internet connection for package installation

### Recommended Requirements
- **Python**: 3.9 or 3.10
- **RAM**: 2GB available memory
- **Storage**: 1GB free disk space
- **CPU**: Multi-core processor for large log files

## Installation Methods

### Method 1: Quick Setup (Recommended)

#### Windows
1. **Download Python** from https://python.org (3.8+)
2. **Open PowerShell as Administrator**
3. **Run the setup script**:
   ```powershell
   cd "path\to\bot-traffic-analyzer"
   .\setup.ps1
   ```

#### Linux/macOS
1. **Ensure Python 3.8+ is installed**:
   ```bash
   python3 --version
   ```
2. **Run the setup script**:
   ```bash
   cd /path/to/bot-traffic-analyzer
   python3 setup.py
   ```

### Method 2: Manual Installation

1. **Clone or download the project**
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Create necessary directories**:
   ```bash
   mkdir -p output logs data/input data/output
   ```
4. **Test the installation**:
   ```bash
   python src/main_analyzer.py --help
   ```

### Method 3: Docker Installation

1. **Install Docker** from https://docker.com
2. **Build the container**:
   ```bash
   docker build -t bot-traffic-analyzer .
   ```
3. **Run analysis**:
   ```bash
   docker run -v $(pwd)/logs:/app/logs -v $(pwd)/output:/app/output \
     bot-traffic-analyzer /app/logs/your_log_file.log
   ```

## Dependency Installation

### Core Dependencies (Required)
```bash
pip install pandas>=1.5.0 numpy>=1.20.0 python-dateutil>=2.8.0
```

### Optional Dependencies (Enhanced Features)
```bash
# For visualization charts
pip install matplotlib>=3.5.0 seaborn>=0.11.0

# For advanced analytics
pip install scikit-learn>=1.1.0

# For development and testing
pip install pytest>=7.0.0 black>=22.0.0 flake8>=5.0.0
```

## Platform-Specific Instructions

### Windows

#### PowerShell Execution Policy
If you encounter execution policy errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Windows Defender
Add the project directory to Windows Defender exclusions if scanning slows down analysis.

#### Path Issues
Ensure Python is in your PATH:
```cmd
python --version
pip --version
```

### Linux

#### Ubuntu/Debian
```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip

# Install project dependencies
pip3 install -r requirements.txt
```

#### CentOS/RHEL
```bash
# Install Python and pip
sudo yum install python3 python3-pip

# Install project dependencies
pip3 install -r requirements.txt
```

### macOS

#### Using Homebrew
```bash
# Install Python
brew install python

# Install project dependencies
pip3 install -r requirements.txt
```

#### Using pyenv (Recommended)
```bash
# Install pyenv
brew install pyenv

# Install Python 3.9
pyenv install 3.9.16
pyenv global 3.9.16

# Install dependencies
pip install -r requirements.txt
```

## Verification

### Test Installation
```bash
# Run system test
python test_system.py

# Analyze sample data
python src/main_analyzer.py sample_logs.txt
```

### Expected Output
```
🧪 Running Bot Detection System Test
==================================================
✅ Generated 2000 log entries in test_access.log
🔍 Starting analysis of: test_access.log
📝 Parsing log entries...
✅ Parsed 2000 log entries
📊 Analyzing traffic patterns...
🔎 Analyzed 9 unique IP addresses
🤖 Running bot detection...
🎯 Detected 4 bots out of 9 IPs
✅ Test completed successfully!
```

## Troubleshooting

### Common Issues

#### "Python not found"
- **Windows**: Install from python.org and ensure "Add to PATH" is checked
- **Linux**: Install python3 package for your distribution
- **macOS**: Install via Homebrew or download from python.org

#### "pip not found"
```bash
# Linux/macOS
python3 -m ensurepip --upgrade

# Windows
python -m ensurepip --upgrade
```

#### "Permission denied"
```bash
# Use user installation
pip install --user -r requirements.txt

# Or use virtual environment
python -m venv bot_analyzer_env
source bot_analyzer_env/bin/activate  # Linux/macOS
bot_analyzer_env\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### "ModuleNotFoundError"
```bash
# Ensure you're in the project directory
cd /path/to/bot-traffic-analyzer

# Install missing dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Large Log Files (Memory Issues)
```bash
# Use system monitoring
# Linux/macOS
htop

# Windows
Task Manager

# Increase virtual memory if needed
# Consider processing logs in chunks
```

### Performance Optimization

#### For Large Log Files (>100MB)
1. **Increase available memory**
2. **Process in chunks**:
   ```bash
   split -l 100000 large_log.txt chunk_
   for chunk in chunk_*; do
       python src/main_analyzer.py "$chunk"
   done
   ```
3. **Use SSD storage** for faster I/O

#### For High-Frequency Analysis
1. **Use cron jobs** for scheduled analysis
2. **Implement log rotation**
3. **Set up automated cleanup**:
   ```bash
   # Add to crontab
   0 2 * * * /path/to/cleanup_old_results.sh
   ```

## Production Deployment

### Automated Installation Script
```bash
#!/bin/bash
# production_install.sh

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip nginx -y

# Create service user
sudo useradd -r -s /bin/false bot_analyzer

# Install application
cd /opt
sudo git clone <repository> bot-traffic-analyzer
cd bot-traffic-analyzer
sudo pip3 install -r requirements.txt

# Set permissions
sudo chown -R bot_analyzer:bot_analyzer /opt/bot-traffic-analyzer

# Install systemd service
sudo cp scripts/bot-analyzer.service /etc/systemd/system/
sudo systemctl enable bot-analyzer
sudo systemctl start bot-analyzer
```

### Environment Variables
```bash
# .env file
LOG_DIRECTORY=/var/log/nginx
OUTPUT_DIRECTORY=/var/log/bot-analyzer
ANALYSIS_INTERVAL=3600
EMAIL_ALERTS=admin@company.com
SLACK_WEBHOOK=https://hooks.slack.com/...
```

### Security Considerations
1. **Run as non-root user**
2. **Set proper file permissions**
3. **Enable firewall rules**
4. **Regular security updates**
5. **Log rotation and cleanup**

## Support

### Getting Help
1. **Check README.md** for basic usage
2. **Review USAGE_GUIDE.md** for detailed instructions
3. **Run built-in tests** to verify installation
4. **Check system logs** for error details

### Reporting Issues
Include the following information:
- Operating system and version
- Python version
- Error messages and stack traces
- Log file format and size
- System specifications

### Performance Tuning
Monitor these metrics:
- **Memory usage** during analysis
- **CPU utilization** for large files
- **Disk I/O** for storage bottlenecks
- **Analysis time** for different log sizes

## Next Steps

After successful installation:
1. **Review configuration** in `config/settings.py`
2. **Test with sample data** using `sample_logs.txt`
3. **Analyze your log files** with `python src/main_analyzer.py`
4. **Set up monitoring** for ongoing protection
5. **Implement recommended actions** from analysis reports
