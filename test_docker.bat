@echo off
REM Docker Test Script for Traffic Analyzer (Windows)
REM Tests if the containerized system works correctly

echo 🐳 Testing Docker Container Build ^& Execution
echo =============================================

REM Test 1: Check if Docker is available
echo 📋 Step 1: Checking Docker availability...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker not found. Please install Docker Desktop.
    echo    Download: https://www.docker.com/products/docker-desktop/
    exit /b 1
)

echo ✅ Docker found
docker --version

REM Test 2: Build the container
echo.
echo 🏗️ Step 2: Building traffic analyzer container...
docker build -t traffic-analyzer-pro .
if %errorlevel% neq 0 (
    echo ❌ Container build failed
    exit /b 1
)
echo ✅ Container built successfully

REM Test 3: Run analysis
echo.
echo 📊 Step 3: Running traffic analysis in container...
docker run --rm -v %cd%/output:/app/output traffic-analyzer-pro test_access.log
if %errorlevel% neq 0 (
    echo ❌ Analysis failed
    exit /b 1
)
echo ✅ Analysis completed successfully

REM Test 4: Verify outputs
echo.
echo 🔍 Step 4: Verifying generated outputs...
if exist "output" (
    echo ✅ Output directory found
    dir output /b | findstr /R "dashboard.*\.png"
    dir output /b | findstr /R ".*\.csv"
    dir output /b | findstr /R ".*\.json"
) else (
    echo ❌ No output directory found
    exit /b 1
)

echo.
echo 🎉 SUCCESS! Docker container execution completed.
echo 📁 Check the output/ directory for your professional reports.
echo.
echo 🚀 To run again:
echo    docker run --rm -v %cd%/output:/app/output traffic-analyzer-pro test_access.log
