#!/bin/bash

# Frontend Setup Script for Multilingual Education Platform

echo "🚀 Setting up Multilingual Education Platform Frontend..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm version: $(npm --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Dependencies installed successfully!"
echo ""

# Create fonts directory if it doesn't exist
mkdir -p public/fonts

echo "📝 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Download OpenDyslexic font from https://opendyslexic.org/"
echo "2. Place OpenDyslexic-Regular.woff2 in public/fonts/"
echo "3. Ensure backend API is running on http://localhost:5000"
echo "4. Run 'npm run dev' to start the development server"
echo ""
echo "For accessibility testing:"
echo "- Run 'npm run a11y' (requires dev server to be running)"
echo ""
echo "Happy coding! 🎉"
