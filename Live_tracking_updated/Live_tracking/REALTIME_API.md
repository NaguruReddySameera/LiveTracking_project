# Real-time Vessel Tracking API Documentation

## Overview
The Maritime Vessel Tracking Platform now includes comprehensive real-time data APIs and WebSocket support for live updates across all components: vessels, ships, analyst data, and notifications.

## Architecture

### Backend Components

#### 1. Real-time REST APIs (`backend/apps/vessels/realtime_views.py`)
Located at `/vessels/realtime/*` endpoints

**Endpoints:**
- `GET /vessels/realtime/vessels/` - Get all vessel positions in real-time
- `GET /vessels/realtime/ships/` - Get comprehensive ships list with status
- `GET /vessels/realtime/analyst/` - Get real-time analytics data for analysts
- `GET /vessels/realtime/notifications/` - Get user's real-time notifications
- `GET /vessels/realtime/positions/` - Get vessel position history/stream
- `GET /vessels/realtime/fleet-health/` - Get fleet health and status metrics

#### 2. WebSocket Server (`backend/realtime_server.py`)
Runs on port `5000` with Flask-SocketIO

**Socket Events:**
- `connect` - Client connects to WebSocket
- `disconnect` - Client disconnects
- `subscribe:vessels` - Subscribe to live vessel updates
- `subscribe:ships` - Subscribe to ships list updates
- `subscribe:analyst` - Subscribe to analyst data updates
- `subscribe:notifications` - Subscribe to notification updates
- `subscribe:health` - Subscribe to fleet health updates
- `unsubscribe` - Unsubscribe from a channel
- `request:vessel` - Request specific vessel data

**Emitted Events:**
- `vessel:update` - Real-time vessel position updates
- `ships:update` - Ships list updates
- `analyst:update` - Analyst data updates
- `notifications:update` - Notification updates
- `health:update` - Fleet health updates

#### 3. Background Tasks (`backend/apps/vessels/management/commands/update_realtime_data.py`)
Generates simulated vessel movements and notifications

**Functions:**
- `update_vessel_positions()` - Simulates vessel movement with random position changes
- `create_random_notifications()` - Creates sample notifications for events
- `cleanup_old_notifications()` - Removes notifications older than 30 days

### Frontend Components

#### 1. Enhanced Socket Service (`frontend/src/services/socket.ts`)
Manages WebSocket connections and subscriptions

**Key Functions:**
```typescript
connectSocket(): Socket - Establish WebSocket connection
subscribeVessels(callback?): void - Subscribe to vessel updates
subscribeShips(callback?): void - Subscribe to ships updates
subscribeAnalyst(callback?): void - Subscribe to analyst data
subscribeNotifications(callback?): void - Subscribe to notifications
subscribeFleetHealth(callback?): void - Subscribe to fleet health

onVesselUpdate(callback): void - Listen for vessel updates
onShipsUpdate(callback): void - Listen for ships updates
onAnalystUpdate(callback): void - Listen for analyst updates
onFleetHealthUpdate(callback): void - Listen for health updates

unsubscribeVessels/Ships/Analyst/Notifications/FleetHealth(): void - Unsubscribe
disconnectSocket(): void - Disconnect WebSocket
```

#### 2. Realtime Service (`frontend/src/services/realtimeService.ts`)
REST API wrapper for real-time endpoints

**Methods:**
```typescript
getRealtimeVessels(): Promise<RealtimeVesselData[]>
getRealtimeShips(): Promise<RealtimeShipData[]>
getAnalystData(): Promise<AnalystDataResponse>
getRealtimeNotifications(): Promise<any>
getVesselPositionStream(vesselId?): Promise<any>
getFleetHealth(): Promise<FleetHealthStatus>
createNotification(notificationData): Promise<any>
```

#### 3. Dashboard Components

**OperatorDashboard.tsx** - Enhanced with real-time subscriptions
- Displays live vessel positions on Leaflet map
- Real-time subscription to vessel and fleet health updates
- Fallback polling every 30 seconds

**AnalystDashboard.tsx** (NEW) - Real-time analytics
- Live fleet statistics
- Speed analytics (average, max, min)
- Status and type distribution charts
- Movement patterns (underway, anchored, moored)
- Geographic distribution of vessels
- Voyage information

**RealtimeNotifications.tsx** (NEW) - Real-time notification center
- Live notification streaming
- Filters by type (alert, warning, info, success)
- Unread notification tracking
- Time-based notification display (just now, 5m ago, etc.)

## Setup Instructions

### 1. Install Dependencies

Backend:
```bash
cd backend
pip install -r requirements.txt
```

Frontend:
```bash
cd frontend
npm install socket.io-client  # Already included
```

### 2. Start Real-time Server

```bash
cd backend
python realtime_server.py
```

The Socket.io server will start on `http://localhost:5000`

### 3. Start Background Tasks (Optional - for simulated data)

```bash
cd backend
python manage.py update_realtime_data
```

Or schedule it with Celery for periodic execution:
```python
# In maritime_project/settings.py
CELERY_BEAT_SCHEDULE = {
    'update-realtime-data': {
        'task': 'apps.vessels.tasks.update_realtime_data',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}
```

### 4. Configure Environment Variables

Create `.env` file in backend:
```
FLASK_SECRET_KEY=your-secret-key-here
REACT_APP_SOCKET_URL=http://localhost:5000
```

### 5. Start All Services

Terminal 1 - Django Backend:
```bash
cd backend
python manage.py runserver 0.0.0.0:8000
```

Terminal 2 - React Frontend:
```bash
cd frontend
npm start
```

Terminal 3 - WebSocket Server:
```bash
cd backend
python realtime_server.py
```

## Data Models

### RealtimeVesselData
```typescript
{
  id: number;
  mmsi: string;
  name: string;
  type: string;
  status: string;
  flag_country: string;
  position: {
    latitude: number;
    longitude: number;
    speed: number;
    heading: number;
    course: number;
    updated_at: string;
  };
  destination?: string;
  eta?: string;
  is_tracked: boolean;
  last_update: string;
}
```

### AnalystDataResponse
```typescript
{
  summary: {
    total_vessels: number;
    active_vessels: number;
    inactive_vessels: number;
    updated_last_24h: number;
  };
  status_breakdown: Array<{status: string; count: number}>;
  type_breakdown: Array<{type: string; count: number}>;
  movement: {underway: number; anchored: number; moored: number};
  speed_analytics: {average: number; maximum: number; minimum: number};
  geography: Array<{country: string; count: number}>;
  voyage: {with_destination: number; without_destination: number};
}
```

### FleetHealthStatus
```typescript
{
  fleet_status: {
    healthy: number;
    warning: number;
    critical: number;
    stale_data: number;
  };
  communication: {
    active: number;
    inactive: number;
  };
  total_vessels: number;
}
```

## Example Usage

### Subscribe to Vessel Updates (React)
```typescript
import { useEffect } from 'react';
import { subscribeVessels, onVesselUpdate } from '../services/socket';

export const MyComponent = () => {
  useEffect(() => {
    // Subscribe to vessel updates
    subscribeVessels();
    
    // Listen for updates
    onVesselUpdate((data) => {
      console.log('Vessel update:', data.data);
      // Update UI with new vessel positions
    });
  }, []);

  return <div>Vessel Tracking</div>;
};
```

### Get Analyst Data
```typescript
import realtimeService from '../services/realtimeService';

async function loadAnalytics() {
  const analyticsData = await realtimeService.getAnalystData();
  console.log('Analytics:', analyticsData);
  // Use data for charts and statistics
}
```

### Create Notification (Admin Only)
```typescript
import realtimeService from '../services/realtimeService';

async function createAlert(vesselId: number) {
  await realtimeService.createNotification({
    type: 'alert',
    title: 'Speed Alert',
    message: 'Vessel speed exceeds threshold',
    vessel_id: vesselId
  });
}
```

## Performance Optimization

1. **Compression**: WebSocket messages are automatically compressed
2. **Reconnection**: Automatic reconnection with exponential backoff
3. **Polling Fallback**: REST API fallback when WebSocket unavailable
4. **Selective Updates**: Only subscribed channels receive updates
5. **Message Throttling**: Updates limited to prevent overwhelming clients

## Security

- All endpoints require authentication (IsAuthenticated)
- Role-based access control:
  - Operators: Can view vessels, ships, and health status
  - Analysts: Can view all data including analytics
  - Admins: Full access including creating notifications
- WebSocket connections validated on subscription

## Monitoring

### Check WebSocket Connection Status
```typescript
import { isSocketConnected, getSocket } from '../services/socket';

if (isSocketConnected()) {
  console.log('WebSocket connected');
  const socket = getSocket();
  console.log('Socket ID:', socket?.id);
}
```

### Monitor Notification Performance
```bash
cd backend
python manage.py shell
>>> from apps.notifications.models import Notification
>>> Notification.objects.filter(is_read=False).count()  # Unread count
```

## Troubleshooting

### WebSocket Connection Fails
1. Ensure `realtime_server.py` is running on port 5000
2. Check CORS configuration in `realtime_server.py`
3. Verify `REACT_APP_SOCKET_URL` environment variable

### No Real-time Updates
1. Check if subscriptions are active: `isSocketConnected()`
2. Verify REST API endpoints return data: `getRealtimeVessels()`
3. Run background task to generate data: `python manage.py update_realtime_data`

### High Latency
1. Increase polling interval in components
2. Reduce notification creation frequency
3. Check server resource usage

## Future Enhancements

1. **Data Persistence**: Store streaming data in time-series database (InfluxDB, TimescaleDB)
2. **Advanced Analytics**: Machine learning for anomaly detection
3. **Predictive Routing**: AI-powered route optimization
4. **Mobile Notifications**: Push notifications to mobile devices
5. **Real Data Integration**: Connect to actual AIS/MarineTraffic APIs
6. **Custom Alerts**: User-defined alerting rules
7. **Data Export**: Export streaming data to formats (CSV, JSON, Parquet)

## References

- [Socket.io Documentation](https://socket.io/docs/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
- [Django Real-time Best Practices](https://docs.djangoproject.com/en/stable/)
- [React WebSocket Integration](https://react.dev/)

## Support

For issues or questions about real-time features:
1. Check logs: `backend/logs/` and browser console
2. Review this documentation
3. Check GitHub issues
4. Contact development team

---
**Last Updated**: January 2026
**Version**: 1.0.0
