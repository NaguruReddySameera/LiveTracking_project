"""
Real-time Socket.io server for vessel tracking
Handles WebSocket connections and live data streaming
"""

import os
import json
import logging
from datetime import datetime, timedelta
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime_project.settings')
django.setup()

from django.utils import timezone
from django.db.models import Q
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from apps.vessels.models import Vessel
import random

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active connections
active_connections = {
    'vessels': set(),
    'ships': set(),
    'analyst': set(),
    'notifications': set(),
    'health': set(),
}


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print(f'Client {request.sid} connected')
    emit('connection_response', {'data': 'Connected to real-time server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print(f'Client {request.sid} disconnected')
    # Remove from all subscriptions
    for subscription in active_connections.values():
        subscription.discard(request.sid)


@socketio.on('subscribe:vessels')
def subscribe_vessels():
    """Subscribe to real-time vessel updates"""
    active_connections['vessels'].add(request.sid)
    print(f'Client {request.sid} subscribed to vessels')
    emit('subscription_confirmed', {'channel': 'vessels'})
    
    # Send initial data
    send_vessel_update()


@socketio.on('subscribe:ships')
def subscribe_ships():
    """Subscribe to real-time ships data"""
    active_connections['ships'].add(request.sid)
    print(f'Client {request.sid} subscribed to ships')
    emit('subscription_confirmed', {'channel': 'ships'})
    
    # Send initial data
    send_ships_update()


@socketio.on('subscribe:analyst')
def subscribe_analyst():
    """Subscribe to real-time analyst data"""
    active_connections['analyst'].add(request.sid)
    print(f'Client {request.sid} subscribed to analyst data')
    emit('subscription_confirmed', {'channel': 'analyst'})
    
    # Send initial data
    send_analyst_update()


@socketio.on('subscribe:notifications')
def subscribe_notifications():
    """Subscribe to real-time notifications"""
    active_connections['notifications'].add(request.sid)
    print(f'Client {request.sid} subscribed to notifications')
    emit('subscription_confirmed', {'channel': 'notifications'})


@socketio.on('subscribe:health')
def subscribe_health():
    """Subscribe to fleet health status"""
    active_connections['health'].add(request.sid)
    print(f'Client {request.sid} subscribed to fleet health')
    emit('subscription_confirmed', {'channel': 'health'})
    
    # Send initial data
    send_health_update()


@socketio.on('unsubscribe')
def unsubscribe(data):
    """Unsubscribe from a channel"""
    channel = data.get('channel', 'vessels')
    if channel in active_connections:
        active_connections[channel].discard(request.sid)
        print(f'Client {request.sid} unsubscribed from {channel}')


def send_vessel_update():
    """Send real-time vessel position updates"""
    try:
        vessels = Vessel.objects.filter(is_deleted=False, is_tracked=True)
        
        vessel_data = []
        for vessel in vessels:
            # Simulate position movement
            lat_offset = random.uniform(-0.01, 0.01)
            lng_offset = random.uniform(-0.01, 0.01)
            
            data = {
                'id': vessel.id,
                'mmsi': vessel.mmsi,
                'name': vessel.vessel_name,
                'type': vessel.vessel_type,
                'status': vessel.status,
                'position': {
                    'lat': float(vessel.latitude or 0) + lat_offset,
                    'lng': float(vessel.longitude or 0) + lng_offset,
                    'speed': float(vessel.speed_over_ground or 0),
                    'heading': vessel.heading or 0,
                    'course': float(vessel.course_over_ground or 0),
                },
                'destination': vessel.destination,
                'timestamp': timezone.now().isoformat(),
            }
            vessel_data.append(data)
        
        # Emit to all subscribers
        socketio.emit(
            'vessel:update',
            {
                'success': True,
                'count': len(vessel_data),
                'data': vessel_data,
                'timestamp': timezone.now().isoformat(),
            },
            room='vessels',
            skip_sid=[],
            to=[sid for sid in active_connections['vessels']]
        )
    except Exception as e:
        logger.error(f'Error sending vessel update: {e}')


def send_ships_update():
    """Send real-time ships list update"""
    try:
        vessels = Vessel.objects.filter(is_deleted=False, is_tracked=True).order_by('-last_position_update')
        
        ships_data = []
        for ship in vessels:
            ships_data.append({
                'id': ship.id,
                'mmsi': ship.mmsi,
                'name': ship.vessel_name,
                'type': ship.vessel_type,
                'country': ship.flag_country,
                'status': ship.status,
                'position': {
                    'lat': float(ship.latitude or 0),
                    'lng': float(ship.longitude or 0),
                },
                'motion': {
                    'speed': float(ship.speed_over_ground or 0),
                    'heading': ship.heading or 0,
                    'course': float(ship.course_over_ground or 0),
                },
                'lastUpdate': ship.last_position_update.isoformat() if ship.last_position_update else None,
            })
        
        socketio.emit(
            'ships:update',
            {
                'success': True,
                'total': len(ships_data),
                'data': ships_data,
                'timestamp': timezone.now().isoformat(),
            },
            skip_sid=[],
            to=[sid for sid in active_connections['ships']]
        )
    except Exception as e:
        logger.error(f'Error sending ships update: {e}')


def send_analyst_update():
    """Send real-time analyst data update"""
    try:
        vessels = Vessel.objects.filter(is_deleted=False)
        
        total_vessels = vessels.count()
        active_vessels = vessels.filter(is_tracked=True).count()
        
        from django.db.models import Count, Avg, Max, Min
        
        status_breakdown = list(
            vessels.values('status').annotate(count=Count('id')).order_by('-count')
        )
        
        type_breakdown = list(
            vessels.values('vessel_type').annotate(count=Count('id')).order_by('-count')
        )
        
        speed_data = vessels.filter(speed_over_ground__isnull=False).aggregate(
            avg_speed=Avg('speed_over_ground'),
            max_speed=Max('speed_over_ground'),
            min_speed=Min('speed_over_ground')
        )
        
        socketio.emit(
            'analyst:update',
            {
                'success': True,
                'data': {
                    'summary': {
                        'total_vessels': total_vessels,
                        'active_vessels': active_vessels,
                        'inactive_vessels': total_vessels - active_vessels,
                    },
                    'status': [
                        {'status': item['status'], 'count': item['count']}
                        for item in status_breakdown
                    ],
                    'types': [
                        {'type': item['vessel_type'], 'count': item['count']}
                        for item in type_breakdown
                    ],
                    'speed': {
                        'average': round(float(speed_data['avg_speed'] or 0), 2),
                        'max': float(speed_data['max_speed'] or 0),
                        'min': float(speed_data['min_speed'] or 0),
                    },
                },
                'timestamp': timezone.now().isoformat(),
            },
            skip_sid=[],
            to=[sid for sid in active_connections['analyst']]
        )
    except Exception as e:
        logger.error(f'Error sending analyst update: {e}')


def send_health_update():
    """Send real-time fleet health status"""
    try:
        vessels = Vessel.objects.filter(is_deleted=False)
        
        healthy = vessels.filter(status='underway').count()
        warning = vessels.filter(status='at_anchor').count()
        critical = vessels.filter(status='aground').count()
        
        stale_threshold = timezone.now() - timedelta(hours=1)
        stale_vessels = vessels.filter(last_position_update__lt=stale_threshold).count()
        
        recently_updated = vessels.filter(
            last_position_update__gte=timezone.now() - timedelta(minutes=30)
        ).count()
        
        socketio.emit(
            'health:update',
            {
                'success': True,
                'data': {
                    'fleet_status': {
                        'healthy': healthy,
                        'warning': warning,
                        'critical': critical,
                        'stale': stale_vessels,
                    },
                    'communication': {
                        'active': recently_updated,
                        'inactive': vessels.count() - recently_updated,
                    },
                    'total': vessels.count(),
                },
                'timestamp': timezone.now().isoformat(),
            },
            skip_sid=[],
            to=[sid for sid in active_connections['health']]
        )
    except Exception as e:
        logger.error(f'Error sending health update: {e}')


@socketio.on('request:vessel')
def handle_vessel_request(data):
    """Handle specific vessel position request"""
    vessel_id = data.get('vessel_id')
    try:
        vessel = Vessel.objects.get(id=vessel_id)
        emit('vessel:position', {
            'id': vessel.id,
            'name': vessel.vessel_name,
            'position': {
                'lat': float(vessel.latitude or 0),
                'lng': float(vessel.longitude or 0),
                'speed': float(vessel.speed_over_ground or 0),
            },
            'timestamp': timezone.now().isoformat(),
        })
    except Vessel.DoesNotExist:
        emit('error', {'message': f'Vessel {vessel_id} not found'})


if __name__ == '__main__':
    # Run Socket.io server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
