#!/bin/bash
# Docker Test Script for Traffic Analyzer
# Tests if the containerized system works correctly

echo "🐳 Testing Docker Container Build & Execution"
echo "============================================="

# Test 1: Check if Docker is available
echo "📋 Step 1: Checking Docker availability..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop."
    echo "   Download: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

echo "✅ Docker found: $(docker --version)"

# Test 2: Build the container
echo ""
echo "🏗️ Step 2: Building traffic analyzer container..."
if docker build -t traffic-analyzer-pro .; then
    echo "✅ Container built successfully"
else
    echo "❌ Container build failed"
    exit 1
fi

# Test 3: Run analysis
echo ""
echo "📊 Step 3: Running traffic analysis in container..."
if docker run --rm -v "$(pwd)/output:/app/output" traffic-analyzer-pro test_access.log; then
    echo "✅ Analysis completed successfully"
else
    echo "❌ Analysis failed"
    exit 1
fi

# Test 4: Verify outputs
echo ""
echo "🔍 Step 4: Verifying generated outputs..."
if [ -d "output" ] && [ "$(ls -A output)" ]; then
    echo "✅ Output files generated:"
    ls -la output/ | grep -E "(dashboard|csv|json|txt).*$(date +%Y%m%d)"
else
    echo "❌ No output files found"
    exit 1
fi

echo ""
echo "🎉 SUCCESS! Docker container execution completed."
echo "📁 Check the output/ directory for your professional reports."
echo ""
echo "🚀 To run again:"
echo "   docker run --rm -v \$(pwd)/output:/app/output traffic-analyzer-pro test_access.log"
