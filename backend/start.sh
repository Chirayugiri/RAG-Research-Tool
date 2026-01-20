#!/bin/bash

# RAG News Research Tool - Quick Start Script

echo "🚀 Starting RAG News Research Tool..."
echo ""

# Check if .env exists
if [ ! -f "../.env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and add your API keys"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -d "venv/lib" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start FastAPI server
echo "🔥 Starting FastAPI backend server on http://localhost:8000..."
echo "📚 API docs available at http://localhost:8000/docs"
echo ""
python app.py
