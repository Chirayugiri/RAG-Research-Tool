#!/bin/bash

# RAG News Research Tool - Frontend Quick Start Script

echo "🎨 Starting RAG News Research Tool Frontend..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating default .env with localhost backend..."
    echo "VITE_API_URL=http://localhost:8000" > .env
fi

# Start Vite dev server
echo "🔥 Starting React dev server on http://localhost:5173..."
echo ""
npm run dev
