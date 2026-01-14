"""
Background tasks for generating real-time vessel updates
Updates vessel positions and creates sample notifications
"""

import os
import django
import random
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime_project.settings')
django.setup()

from django.utils import timezone
from django.core.management.base import BaseCommand
from apps.vessels.models import Vessel, VesselPosition
from apps.notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()


def update_vessel_positions():
    """
    Simulate vessel movements by updating their positions
    Updates latitude, longitude, speed, and heading
    """
    vessels = Vessel.objects.filter(is_deleted=False, is_tracked=True)
    
    statuses = ['underway', 'at_anchor', 'not_under_command', 'restricted_maneuverability', 'moored', 'aground']
    
    for vessel in vessels:
        try:
            # Random movement simulation
            lat_change = random.uniform(-0.05, 0.05)
            lng_change = random.uniform(-0.05, 0.05)
            
            new_lat = float(vessel.latitude or 0) + lat_change
            new_lng = float(vessel.longitude or 0) + lng_change
            
            # Clamp to valid ranges
            new_lat = max(-90, min(90, new_lat))
            new_lng = max(-180, min(180, new_lng))
            
            # Simulate speed and heading
            vessel.latitude = new_lat
            vessel.longitude = new_lng
            vessel.speed_over_ground = random.uniform(0, 25)  # 0-25 knots
            vessel.heading = random.randint(0, 359)
            vessel.course_over_ground = random.randint(0, 359)
            vessel.status = random.choice(statuses)
            vessel.last_position_update = timezone.now()
            
            vessel.save()
            
            # Create VesselPosition entry for history
            if hasattr(vessel, 'positions'):
                VesselPosition.objects.create(
                    vessel=vessel,
                    latitude=new_lat,
                    longitude=new_lng,
                    speed_over_ground=vessel.speed_over_ground,
                    heading=vessel.heading,
                    course_over_ground=vessel.course_over_ground,
                    timestamp=timezone.now()
                )
            
            print(f"Updated {vessel.vessel_name}: {new_lat:.4f}, {new_lng:.4f}")
        
        except Exception as e:
            print(f"Error updating {vessel.vessel_name}: {e}")


def create_random_notifications():
    """
    Create random notifications for fleet events
    """
    vessels = Vessel.objects.filter(is_deleted=False, is_tracked=True)[:5]
    users = User.objects.filter(groups__name__in=['Analyst', 'Operator'])
    
    if not users.exists():
        return
    
    notification_types = ['alert', 'warning', 'info', 'success']
    event_types = [
        'Speed Alert',
        'Position Update',
        'Status Change',
        'Destination Reached',
        'Geofence Breach',
        'Maintenance Due',
        'Weather Warning',
        'Route Change'
    ]
    
    messages = {
        'Speed Alert': 'Vessel speed exceeds normal threshold',
        'Position Update': 'Vessel position has been updated',
        'Status Change': 'Vessel operational status has changed',
        'Destination Reached': 'Vessel has reached its destination',
        'Geofence Breach': 'Vessel has breached a defined geofence',
        'Maintenance Due': 'Scheduled maintenance is due',
        'Weather Warning': 'Severe weather conditions reported',
        'Route Change': 'Vessel has changed its route'
    }
    
    for user in users:
        for vessel in vessels:
            # 30% chance to create a notification
            if random.random() < 0.3:
                event_type = random.choice(event_types)
                notif_type = 'alert' if event_type in ['Speed Alert', 'Geofence Breach', 'Weather Warning'] else 'warning' if event_type in ['Status Change', 'Maintenance Due'] else 'info'
                
                try:
                    Notification.objects.create(
                        user=user,
                        type=notif_type,
                        title=event_type,
                        message=f"{messages.get(event_type, 'Event occurred')}: {vessel.vessel_name}",
                        vessel=vessel,
                        is_read=False
                    )
                    print(f"Created {notif_type} notification for {user.email}: {event_type}")
                except Exception as e:
                    print(f"Error creating notification: {e}")


def cleanup_old_notifications():
    """
    Clean up notifications older than 30 days
    """
    threshold_date = timezone.now() - timedelta(days=30)
    
    try:
        deleted_count, _ = Notification.objects.filter(
            created_at__lt=threshold_date
        ).delete()
        print(f"Deleted {deleted_count} old notifications")
    except Exception as e:
        print(f"Error cleaning up notifications: {e}")


def run_background_tasks():
    """
    Execute all background tasks
    """
    print(f"\n=== Running background tasks at {timezone.now()} ===")
    print("1. Updating vessel positions...")
    update_vessel_positions()
    
    print("\n2. Creating random notifications...")
    create_random_notifications()
    
    print("\n3. Cleaning up old notifications...")
    cleanup_old_notifications()
    
    print(f"\n=== Background tasks completed ===\n")


class Command(BaseCommand):
    help = 'Run real-time data update background tasks'

    def handle(self, *args, **options):
        run_background_tasks()


if __name__ == '__main__':
    run_background_tasks()
