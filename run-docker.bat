@echo off
echo 🐳 Professional Traffic Analyzer - Docker Version
echo.

if "%1"=="" (
    echo Usage: run-docker.bat log_file.txt
    echo Example: run-docker.bat data/samples/test_sample_100.log
    echo.
    echo Available sample files:
    dir /b data\samples\*.log 2>nul
    exit /b 1
)

echo 📊 Building Docker image...
docker build -t traffic-analyzer . || (
    echo ❌ Docker build failed!
    exit /b 1
)

echo 🚀 Running analysis: %1
docker run --rm ^
  -v "%CD%\data:/app/data:ro" ^
  -v "%CD%\output:/app/output" ^
  traffic-analyzer %1

echo.
echo ✅ Analysis complete! Check output\ directory for results.
echo 📁 Generated files:
dir /b output\*.png output\*.csv output\*.json output\*.txt 2>nul
pause
