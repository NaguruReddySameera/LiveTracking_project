#!/bin/bash

# Local Development Server Startup Script
# Starts both backend and frontend servers

echo "=========================================="
echo "Starting Local Development Servers"
echo "=========================================="

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Creating backend/.env file..."
    echo "MARINESIA_API_KEY=rwcxgUmACAeJJCshUZAbtoOzC" > backend/.env
fi

# Add MarineSia API key to .env if not present
if ! grep -q "MARINESIA_API_KEY" backend/.env; then
    echo "MARINESIA_API_KEY=rwcxgUmACAeJJCshUZAbtoOzC" >> backend/.env
    echo "✅ Added MARINESIA_API_KEY to backend/.env"
fi

# Export environment variable
export MARINESIA_API_KEY=rwcxgUmACAeJJCshUZAbtoOzC

echo ""
echo "🚀 Starting Backend Server..."
echo "   URL: http://localhost:8000"
echo "   API: http://localhost:8000/api"
echo ""

# Start backend in background
cd backend
python manage.py runserver > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Logs: backend.log"
echo ""

# Wait a bit for backend to start
sleep 3

echo "🌐 Starting Frontend Server..."
echo "   URL: http://localhost:3000"
echo ""

# Start frontend
cd frontend
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "   Logs: frontend.log"
echo ""

echo "=========================================="
echo "✅ Both servers are starting!"
echo "=========================================="
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "To stop servers, run:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Or press Ctrl+C and run:"
echo "  pkill -f 'manage.py runserver'"
echo "  pkill -f 'react-scripts start'"
echo ""
echo "Testing API..."
sleep 5

# Test API endpoint
echo ""
echo "🧪 Testing API endpoint..."
echo ""

# Try to get demo users (no auth required)
curl -s http://localhost:8000/api/auth/demo-users/ | python3 -m json.tool 2>/dev/null || echo "Backend not ready yet. Wait a few seconds and try again."

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="

