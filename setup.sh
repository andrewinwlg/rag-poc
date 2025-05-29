#!/bin/bash

echo "🚀 Setting up Local RAG POC..."
echo "================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose > /dev/null 2>&1 && ! docker compose version > /dev/null 2>&1; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker is running"

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    mkdir -p data
    echo "📁 Created data directory"
fi

# Check if there are any files in data directory
if [ -z "$(ls -A data)" ]; then
    echo "📄 No documents found in data/ directory"
    echo "   Sample documents have been created for you!"
else
    echo "📄 Found documents in data/ directory"
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if command -v pip3 > /dev/null 2>&1; then
    pip3 install -r requirements.txt
elif command -v pip > /dev/null 2>&1; then
    pip install -r requirements.txt
else
    echo "❌ pip not found. Please install Python and pip first."
    exit 1
fi

echo "✅ Python dependencies installed"

# Make rag.py executable
chmod +x rag.py

echo ""
echo "🎉 Setup complete! Next steps:"
echo "================================"
echo "1. Start the system:"
echo "   docker compose up --build"
echo ""
echo "2. Wait for all services to start (especially Ollama model download)"
echo ""
echo "3. In another terminal, ask questions:"
echo "   python rag.py \"What is this system about?\""
echo "   python rag.py \"How do I troubleshoot issues?\""
echo ""
echo "4. Use --verbose flag for detailed output:"
echo "   python rag.py --verbose \"Your question here\""
echo ""
echo "📚 Check README.md for more information and troubleshooting tips." 