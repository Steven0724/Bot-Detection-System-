#!/bin/bash
echo "🐳 Professional Traffic Analyzer - Docker Version"
echo

if [ -z "$1" ]; then
    echo "Usage: ./run-docker.sh log_file.txt"
    echo "Example: ./run-docker.sh data/samples/sample.log"
    echo
    echo "Available commands:"
    echo "  ./run-docker.sh --help                   Show analyzer help"
    echo "  ./run-docker.sh data/samples/sample.log  Analyze sample data"
    echo
    echo "Note: The container includes a built-in sample.log for testing"
    exit 1
fi

echo "📊 Building Docker image..."
if ! docker build -t traffic-analyzer .; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "🚀 Running analysis: $1"
docker run --rm \
  -v "$(pwd)/output:/app/output" \
  traffic-analyzer "$1"

echo
echo "✅ Analysis complete! Check output/ directory for results."
echo "📁 Generated files:"
ls -la output/*.{png,csv,json,txt} 2>/dev/null || echo "No output files found"
