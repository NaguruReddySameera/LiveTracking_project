"""
Real-time API views for vessel tracking
Provides live data streams for vessels, ships, analyst data, and notifications
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from django.db.models import Q, Count, F, Avg, Max, Min
import random
from datetime import datetime, timedelta
import logging

from apps.authentication.permissions import IsOperator, IsAnalyst, IsAdmin
from .models import Vessel, VesselPosition
from .serializers import VesselDetailSerializer, VesselPositionSerializer

logger = logging.getLogger(__name__)


class RealtimeVesselsAPI(APIView):
    """
    Real-time vessel position updates
    GET: Returns all vessels with current positions for live tracking
    """
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        """Get all vessels with current positions and real-time data"""
        vessels = Vessel.objects.filter(
            is_deleted=False,
            is_tracked=True
        ).select_related().prefetch_related('positions')
        
        vessel_data = []
        for vessel in vessels:
            latest_position = vessel.positions.latest('timestamp') if vessel.positions.exists() else None
            
            data = {
                'id': vessel.id,
                'mmsi': vessel.mmsi,
                'name': vessel.vessel_name,
                'type': vessel.vessel_type,
                'status': vessel.status,
                'flag_country': vessel.flag_country,
                'position': {
                    'latitude': float(vessel.latitude) if vessel.latitude else None,
                    'longitude': float(vessel.longitude) if vessel.longitude else None,
                    'speed': float(vessel.speed_over_ground) if vessel.speed_over_ground else 0,
                    'heading': vessel.heading or 0,
                    'course': float(vessel.course_over_ground) if vessel.course_over_ground else 0,
                    'updated_at': vessel.last_position_update.isoformat() if vessel.last_position_update else None,
                },
                'destination': vessel.destination,
                'eta': vessel.eta.isoformat() if vessel.eta else None,
                'is_tracked': vessel.is_tracked,
                'last_update': vessel.last_position_update.isoformat() if vessel.last_position_update else None,
            }
            vessel_data.append(data)
        
        return Response({
            'success': True,
            'count': len(vessel_data),
            'timestamp': timezone.now().isoformat(),
            'data': vessel_data
        })


class RealtimeShipsAPI(APIView):
    """
    Real-time ships list with status updates
    Provides comprehensive ship information with live updates
    """
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        """Get all ships with real-time status"""
        vessels = Vessel.objects.filter(
            is_deleted=False,
            is_tracked=True
        ).values(
            'id', 'mmsi', 'vessel_name', 'vessel_type', 'flag_country',
            'status', 'latitude', 'longitude', 'speed_over_ground',
            'heading', 'course_over_ground', 'destination', 'eta',
            'last_position_update', 'gross_tonnage', 'call_sign'
        ).order_by('-last_position_update')
        
        ships_data = []
        for ship in vessels:
            ships_data.append({
                'id': ship['id'],
                'mmsi': ship['mmsi'],
                'name': ship['vessel_name'],
                'type': ship['vessel_type'],
                'callSign': ship['call_sign'],
                'country': ship['flag_country'],
                'status': ship['status'],
                'tonnage': ship['gross_tonnage'],
                'position': {
                    'lat': float(ship['latitude']) if ship['latitude'] else None,
                    'lng': float(ship['longitude']) if ship['longitude'] else None,
                },
                'motion': {
                    'speed': float(ship['speed_over_ground']) if ship['speed_over_ground'] else 0,
                    'heading': ship['heading'] or 0,
                    'course': float(ship['course_over_ground']) if ship['course_over_ground'] else 0,
                },
                'voyage': {
                    'destination': ship['destination'],
                    'eta': ship['eta'].isoformat() if ship['eta'] else None,
                },
                'lastUpdate': ship['last_position_update'].isoformat() if ship['last_position_update'] else None,
            })
        
        return Response({
            'success': True,
            'total': len(ships_data),
            'timestamp': timezone.now().isoformat(),
            'data': ships_data
        })


class AnalystDataRealtimeAPI(APIView):
    """
    Real-time analytics data for analysts
    Provides live statistics, trends, and insights
    """
    permission_classes = [IsAuthenticated, IsAnalyst]
    
    def get(self, request):
        """Get real-time analyst data"""
        vessels = Vessel.objects.filter(is_deleted=False)
        
        # Vessel statistics
        total_vessels = vessels.count()
        active_vessels = vessels.filter(is_tracked=True).count()
        inactive_vessels = vessels.filter(is_tracked=False).count()
        
        # Status breakdown
        status_breakdown = list(
            vessels.values('status').annotate(count=Count('id')).order_by('-count')
        )
        
        # Vessel type breakdown
        type_breakdown = list(
            vessels.values('vessel_type').annotate(count=Count('id')).order_by('-count')
        )
        
        # Speed analytics
        speed_data = vessels.filter(speed_over_ground__isnull=False).aggregate(
            avg_speed=Avg('speed_over_ground'),
            max_speed=Max('speed_over_ground'),
            min_speed=Min('speed_over_ground')
        )
        
        # Country breakdown
        country_breakdown = list(
            vessels.values('flag_country').annotate(count=Count('id')).order_by('-count')[:10]
        )
        
        # Underway vessels
        underway_vessels = vessels.filter(status='underway').count()
        anchored_vessels = vessels.filter(status='at_anchor').count()
        moored_vessels = vessels.filter(status='moored').count()
        
        # Movement patterns (last 24 hours)
        last_24h = timezone.now() - timedelta(hours=24)
        updated_last_24h = vessels.filter(last_position_update__gte=last_24h).count()
        
        # Average voyage time
        with_destination = vessels.filter(destination__isnull=False).count()
        without_destination = vessels.filter(destination__isnull=True).count()
        
        return Response({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            'data': {
                'summary': {
                    'total_vessels': total_vessels,
                    'active_vessels': active_vessels,
                    'inactive_vessels': inactive_vessels,
                    'updated_last_24h': updated_last_24h,
                },
                'status_breakdown': [
                    {'status': item['status'], 'count': item['count']}
                    for item in status_breakdown
                ],
                'type_breakdown': [
                    {'type': item['vessel_type'], 'count': item['count']}
                    for item in type_breakdown
                ],
                'movement': {
                    'underway': underway_vessels,
                    'anchored': anchored_vessels,
                    'moored': moored_vessels,
                },
                'speed_analytics': {
                    'average': round(float(speed_data['avg_speed'] or 0), 2),
                    'maximum': float(speed_data['max_speed'] or 0),
                    'minimum': float(speed_data['min_speed'] or 0),
                },
                'geography': [
                    {'country': item['flag_country'], 'count': item['count']}
                    for item in country_breakdown
                ],
                'voyage': {
                    'with_destination': with_destination,
                    'without_destination': without_destination,
                }
            }
        })


class RealtimeNotificationsAPI(APIView):
    """
    Real-time notifications API
    Provides live notifications for vessel events
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's real-time notifications"""
        from apps.notifications.models import Notification
        
        user = request.user
        notifications = Notification.objects.filter(user=user).order_by('-created_at')[:50]
        
        unread_count = notifications.filter(is_read=False).count()
        
        notification_data = []
        for notif in notifications:
            notification_data.append({
                'id': notif.id,
                'type': notif.type,
                'title': notif.title,
                'message': notif.message,
                'vessel_id': notif.vessel_id,
                'vessel_name': notif.vessel.vessel_name if notif.vessel else None,
                'is_read': notif.is_read,
                'created_at': notif.created_at.isoformat(),
                'read_at': notif.read_at.isoformat() if notif.read_at else None,
            })
        
        # Group by type
        by_type = {}
        for notif in notification_data:
            notif_type = notif['type']
            if notif_type not in by_type:
                by_type[notif_type] = 0
            by_type[notif_type] += 1
        
        return Response({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            'data': {
                'notifications': notification_data,
                'unread_count': unread_count,
                'by_type': by_type,
            }
        })


class VesselPositionStreamAPI(APIView):
    """
    Streaming vessel positions with mock real-time updates
    For demonstration purposes - generates live position updates
    """
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        """Get live position updates with simulated movement"""
        vessel_id = request.query_params.get('vessel_id')
        
        if vessel_id:
            try:
                vessel = Vessel.objects.get(id=vessel_id, is_deleted=False)
            except Vessel.DoesNotExist:
                return Response(
                    {'success': False, 'error': 'Vessel not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get position history
            positions = vessel.positions.all().order_by('-timestamp')[:10]
            
            position_data = []
            for pos in positions:
                position_data.append({
                    'latitude': float(pos.latitude),
                    'longitude': float(pos.longitude),
                    'speed': float(pos.speed_over_ground or 0),
                    'heading': pos.heading or 0,
                    'timestamp': pos.timestamp.isoformat(),
                })
            
            return Response({
                'success': True,
                'vessel_id': vessel.id,
                'vessel_name': vessel.vessel_name,
                'positions': position_data,
                'timestamp': timezone.now().isoformat(),
            })
        
        # Return all vessel positions
        vessels = Vessel.objects.filter(is_deleted=False, is_tracked=True)
        
        positions_by_vessel = {}
        for vessel in vessels:
            latest = vessel.positions.latest('timestamp') if vessel.positions.exists() else None
            if latest:
                positions_by_vessel[vessel.id] = {
                    'vessel_name': vessel.vessel_name,
                    'position': {
                        'latitude': float(latest.latitude),
                        'longitude': float(latest.longitude),
                        'speed': float(latest.speed_over_ground or 0),
                    },
                    'timestamp': latest.timestamp.isoformat(),
                }
        
        return Response({
            'success': True,
            'total': len(positions_by_vessel),
            'data': positions_by_vessel,
            'timestamp': timezone.now().isoformat(),
        })


class FleetHealthStatusAPI(APIView):
    """
    Real-time fleet health and status monitoring
    """
    permission_classes = [IsAuthenticated, IsOperator]
    
    def get(self, request):
        """Get fleet health metrics"""
        vessels = Vessel.objects.filter(is_deleted=False)
        
        # Health indicators
        healthy = vessels.filter(status='underway').count()
        warning = vessels.filter(status='at_anchor').count()
        critical = vessels.filter(status='aground').count()
        
        # Update frequency check
        stale_threshold = timezone.now() - timedelta(hours=1)
        stale_vessels = vessels.filter(last_position_update__lt=stale_threshold).count()
        
        # Vessel states
        state_summary = {
            'healthy': healthy,
            'warning': warning,
            'critical': critical,
            'stale_data': stale_vessels,
        }
        
        # Communication status
        recently_updated = vessels.filter(
            last_position_update__gte=timezone.now() - timedelta(minutes=30)
        ).count()
        
        communication = {
            'active': recently_updated,
            'inactive': vessels.count() - recently_updated,
        }
        
        return Response({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            'data': {
                'fleet_status': state_summary,
                'communication': communication,
                'total_vessels': vessels.count(),
            }
        })
