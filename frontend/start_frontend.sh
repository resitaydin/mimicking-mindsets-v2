#!/bin/bash

echo "🚀 Starting Mimicking Mindsets Frontend..."
echo "================================================"

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found. Please run this script from the frontend directory."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

echo ""
echo "📋 Frontend Configuration:"
echo "   • Framework: React + Vite"
echo "   • Port: 5173 (default)"
echo "   • Backend API: http://localhost:8000"
echo ""
echo "🌐 Access URL: http://localhost:5173"
echo "================================================"
echo ""

# Start the development server
npm run dev 