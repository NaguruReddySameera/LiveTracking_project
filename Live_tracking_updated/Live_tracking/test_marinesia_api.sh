#!/bin/bash

# Test MarineSia API Integration

echo "=========================================="
echo "Testing MarineSia API Integration"
echo "=========================================="
echo ""

# Set API key
export MARINESIA_API_KEY=rwcxgUmACAeJJCshUZAbtoOzC

# Backend URL
BACKEND_URL="http://localhost:8000"

echo "1. Testing Backend Health..."
curl -s "$BACKEND_URL/api/health/" | python3 -m json.tool 2>/dev/null || echo "❌ Backend not running. Start with: cd backend && python manage.py runserver"
echo ""

echo "2. Getting Demo Users..."
curl -s "$BACKEND_URL/api/auth/demo-users/" | python3 -m json.tool 2>/dev/null || echo "❌ Cannot connect to backend"
echo ""

echo "3. Testing Login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/login/" \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "operator@maritimetracking.com",
    "password": "Operator@123"
  }')

echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"
echo ""

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('access_token', '') or data.get('data', {}).get('access', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Could not get access token. Check login credentials."
    exit 1
fi

echo "✅ Got access token"
echo ""

echo "4. Testing Real-Time Vessels (North Sea)..."
echo "   Area: 50-60°N, -10 to 10°E"
echo ""

VESSELS_RESPONSE=$(curl -s "$BACKEND_URL/api/vessels/realtime_positions/?min_lat=50&max_lat=60&min_lon=-10&max_lon=10" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'accept: application/json')

echo "$VESSELS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$VESSELS_RESPONSE"
echo ""

# Check if MarineSia vessels are in response
if echo "$VESSELS_RESPONSE" | grep -q "marinesia"; then
    echo "✅ MarineSia API is working! Vessels found with source: marinesia"
else
    echo "⚠️  No MarineSia vessels found. Check:"
    echo "   - MARINESIA_API_KEY is set in backend/.env"
    echo "   - Backend server is running"
    echo "   - API key is valid"
fi

echo ""
echo "=========================================="
echo "Test Complete!"
echo "=========================================="

