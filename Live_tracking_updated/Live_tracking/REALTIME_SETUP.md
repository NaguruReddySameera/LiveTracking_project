# Real-time Vessel Tracking Setup Guide

## Quick Start - 5 Minutes

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm 6+
- Already installed: Docker, git

### Step 1: Install Real-time Dependencies

**Backend:**
```bash
cd backend
pip install Flask==3.0.0 Flask-CORS==4.0.0 Flask-SocketIO==5.3.5 python-socketio==5.10.0 python-engineio==4.8.0
# Or use requirements.txt
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install  # socket.io-client already included
```

### Step 2: Start All Services (Open 3 Terminals)

**Terminal 1 - Django Backend (Port 8000):**
```bash
cd backend
python3 manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - WebSocket Real-time Server (Port 5000):**
```bash
cd backend
python3 realtime_server.py
```

**Terminal 3 - React Frontend (Port 3000):**
```bash
cd frontend
npm start
```

### Step 3: Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api/
- **WebSocket:** ws://localhost:5000

### Step 4: Login with Demo Users

**Admin:**
- Email: sameerareddy583@gmail.com
- Password: admin

**Analyst:**
- Email: analyst@maritimetracking.com
- Password: Analyst@123

**Operator:**
- Email: operator@maritimetracking.com
- Password: Operator@123

## Full Installation

### Backend Setup

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python3 manage.py migrate
   ```

5. **Create demo users:**
   ```bash
   python3 create_demo_users.py
   ```

6. **Create sample vessels:**
   ```bash
   python3 create_sample_vessels.py
   ```

### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file (optional):**
   ```bash
   echo "REACT_APP_SOCKET_URL=http://localhost:5000" > .env.local
   ```

### WebSocket Real-time Server Setup

1. **Install Flask dependencies:**
   ```bash
   pip install Flask Flask-CORS Flask-SocketIO python-socketio python-engineio
   ```

2. **Set environment variable (optional):**
   ```bash
   export FLASK_SECRET_KEY="your-secret-key-here"
   ```

3. **Run the server:**
   ```bash
   python3 realtime_server.py
   ```

## Docker Setup (Optional)

### Build and Run with Docker Compose

```bash
# From root directory
docker-compose -f docker-compose.yml up

# Or for development with hot reload
docker-compose -f docker-compose.dev.yml up
```

## Real-time Features Overview

### 1. Live Vessel Tracking
- **Location:** OperatorDashboard
- **Features:**
  - Real-time vessel positions on map
  - Live speed and heading updates
  - Geofence monitoring
  - Status changes

### 2. Fleet Analytics
- **Location:** AnalystDashboard
- **Features:**
  - Live vessel count statistics
  - Speed analytics (average, min, max)
  - Status distribution charts
  - Vessel type breakdown
  - Geographic distribution

### 3. Real-time Notifications
- **Location:** RealtimeNotifications
- **Features:**
  - Live alert streaming
  - Filter by notification type
  - Unread notification tracking
  - Vessel-specific notifications

### 4. Fleet Health Monitoring
- **Features:**
  - Healthy/Warning/Critical status
  - Communication status (active/inactive)
  - Stale data detection
  - Real-time status updates

## API Endpoints

All endpoints require authentication (JWT token).

### REST API (Django)

```
GET     /vessels/realtime/vessels/         - Get all vessel positions
GET     /vessels/realtime/ships/           - Get ships list
GET     /vessels/realtime/analyst/         - Get analytics data
GET     /vessels/realtime/notifications/   - Get notifications
GET     /vessels/realtime/positions/       - Get position history
GET     /vessels/realtime/fleet-health/    - Get fleet health status
```

### WebSocket Events

**Subscribe:**
```
socket.emit('subscribe:vessels')
socket.emit('subscribe:ships')
socket.emit('subscribe:analyst')
socket.emit('subscribe:notifications')
socket.emit('subscribe:health')
```

**Listen:**
```
socket.on('vessel:update', (data) => {})
socket.on('ships:update', (data) => {})
socket.on('analyst:update', (data) => {})
socket.on('notifications:update', (data) => {})
socket.on('health:update', (data) => {})
```

## Configuration

### Environment Variables

**Backend (`.env`):**
```
DJANGO_SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
FLASK_SECRET_KEY=your-flask-secret-key
```

**Frontend (`.env.local`):**
```
REACT_APP_SOCKET_URL=http://localhost:5000
REACT_APP_API_URL=http://localhost:8000/api
```

## Testing Real-time Features

### 1. Test WebSocket Connection
```bash
# Install wscat globally
npm install -g wscat

# Connect to WebSocket
wscat -c ws://localhost:5000

# In the wscat terminal
{"emit": ["subscribe:vessels"]}
```

### 2. Test REST APIs
```bash
# Get real-time vessels
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/vessels/realtime/vessels/

# Get analytics data
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/vessels/realtime/analyst/
```

### 3. Generate Test Data
```bash
cd backend
python3 manage.py update_realtime_data
```

## Troubleshooting

### WebSocket Connection Issues

**Problem:** "Cannot connect to WebSocket server"
- **Solution:** Ensure `realtime_server.py` is running on port 5000
- **Check:** `lsof -i :5000` (Linux/Mac) or `netstat -ano | findstr :5000` (Windows)

**Problem:** "CORS Error"
- **Solution:** Check CORS settings in `realtime_server.py`
- **Verify:** CORS should allow `http://localhost:3000`

### No Real-time Updates

**Problem:** "Updates not appearing"
- **Solution:** 
  1. Check if subscription was successful
  2. Verify WebSocket connection status
  3. Check browser console for errors
  4. Generate test data: `python3 manage.py update_realtime_data`

### High CPU Usage

**Problem:** "Server using too much CPU"
- **Solution:**
  1. Reduce update frequency in `realtime_server.py`
  2. Increase polling interval in components
  3. Limit number of concurrent connections

### Database Errors

**Problem:** "Vessel not found" or "Database locked"
- **Solution:**
  1. Run migrations: `python3 manage.py migrate`
  2. Create demo data: `python3 create_demo_users.py`
  3. Restart Django server

## Performance Tuning

### Reduce Update Frequency
```typescript
// In socket service
const SOCKET_UPDATE_INTERVAL = 1000; // ms
```

### Optimize Component Re-renders
```typescript
// Use React.memo for large lists
const VesselItem = React.memo(({ vessel }) => {
  return <div>{vessel.name}</div>;
});
```

### Database Query Optimization
```python
# Use select_related and prefetch_related
vessels = Vessel.objects.select_related('notifications').prefetch_related('positions')
```

## Security Considerations

1. **Authentication:** All endpoints require JWT token
2. **Role-based Access:**
   - Operators: View vessels, ships, health
   - Analysts: View all data including analytics
   - Admins: Full access
3. **HTTPS:** Use HTTPS in production
4. **WebSocket Security:** Validate connections on server
5. **Rate Limiting:** Implement to prevent abuse

## Monitoring

### Check System Status
```bash
# Check all processes
ps aux | grep -E 'python|node'

# Check ports
lsof -i -P -n | grep -E '3000|5000|8000'

# Check memory usage
free -h  # Linux
vm_stat  # Mac
```

### View Logs
```bash
# Backend logs
tail -f backend/logs/*.log

# Frontend logs
# Check browser console (F12)

# WebSocket logs
# Terminal where realtime_server.py is running
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Use production database (PostgreSQL)
- [ ] Configure allowed hosts
- [ ] Set strong secret keys
- [ ] Enable HTTPS/WSS
- [ ] Configure CORS properly
- [ ] Set up logging
- [ ] Configure monitoring
- [ ] Set up backups

### Deployment Commands

```bash
# Collect static files
python3 manage.py collectstatic --noinput

# Run migrations
python3 manage.py migrate

# Use production server (gunicorn)
gunicorn maritime_project.wsgi --bind 0.0.0.0:8000 --workers 4

# Use production WebSocket server (Waitress)
waitress-serve --port=5000 realtime_server:app
```

## Additional Resources

- [REALTIME_API.md](./REALTIME_API.md) - Detailed API documentation
- [PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md) - Full project docs
- [Socket.io Documentation](https://socket.io/docs/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)

## Support

For issues or questions:
1. Check the documentation files
2. Review browser console (F12)
3. Check terminal logs
4. Review GitHub issues
5. Contact the development team

---

**Version:** 1.0.0
**Last Updated:** January 2026
**Author:** Maritime Tracking Team
