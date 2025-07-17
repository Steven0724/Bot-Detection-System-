# Bot Traffic Analyzer - Windows PowerShell Setup Script

Write-Host "🚀 Bot Traffic Analyzer Setup (Windows)" -ForegroundColor Green
Write-Host "=" * 50

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "   Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Create directories
Write-Host "📁 Creating directories..."
New-Item -ItemType Directory -Path "output" -Force | Out-Null
New-Item -ItemType Directory -Path "logs" -Force | Out-Null
New-Item -ItemType Directory -Path "test_output" -Force | Out-Null

# Install requirements
Write-Host "📦 Installing Python packages..."
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Requirements installed successfully" -ForegroundColor Green
    } else {
        throw "pip install failed"
    }
} catch {
    Write-Host "⚠️  Manual installation may be required" -ForegroundColor Yellow
    Write-Host "   Run: pip install pandas numpy python-dateutil" -ForegroundColor Yellow
}

# Test the system
if (Test-Path "sample_logs.txt") {
    Write-Host "🧪 Running sample analysis..."
    try {
        python src/main_analyzer.py sample_logs.txt --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Sample analysis completed" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  Sample analysis had issues" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=" * 50
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Quick Start:" -ForegroundColor Cyan
Write-Host "   # Analyze a log file:"
Write-Host "   python src/main_analyzer.py your_log_file.log"
Write-Host ""
Write-Host "   # Run system test:"
Write-Host "   python test_system.py"
Write-Host ""
Write-Host "   # View help:"
Write-Host "   python src/main_analyzer.py --help"
Write-Host ""
Write-Host "📁 Results will be saved in the 'output' directory" -ForegroundColor Yellow
