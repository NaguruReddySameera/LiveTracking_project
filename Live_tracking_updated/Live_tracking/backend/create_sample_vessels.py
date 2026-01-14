#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime_project.settings')
django.setup()

from apps.vessels.models import Vessel

sample_vessels = [
    {
        'mmsi': '211378120',
        'vessel_name': 'NORDIC VOYAGER',
        'vessel_type': 'Cargo',
        'flag_country': 'SE',
        'latitude': 58.5,
        'longitude': 18.0,
        'speed_over_ground': '12.5',
        'course_over_ground': '180.0',
        'heading': 182,
        'destination': 'Rotterdam',
        'status': 'underway'
    },
    {
        'mmsi': '244660050',
        'vessel_name': 'DEEP OCEAN',
        'vessel_type': 'Tanker',
        'flag_country': 'NL',
        'latitude': 51.5,
        'longitude': 5.0,
        'speed_over_ground': '8.3',
        'course_over_ground': '270.0',
        'heading': 272,
        'destination': 'Hamburg',
        'status': 'underway'
    },
    {
        'mmsi': '235067890',
        'vessel_name': 'ARCTIC STAR',
        'vessel_type': 'Fishing',
        'flag_country': 'NO',
        'latitude': 60.5,
        'longitude': 20.0,
        'speed_over_ground': '6.5',
        'course_over_ground': '45.0',
        'heading': 47,
        'destination': 'Bergen',
        'status': 'fishing'
    },
    {
        'mmsi': '636067890',
        'vessel_name': 'ATLANTIC DREAM',
        'vessel_type': 'Passenger',
        'flag_country': 'IT',
        'latitude': 45.0,
        'longitude': 15.0,
        'speed_over_ground': '16.0',
        'course_over_ground': '90.0',
        'heading': 92,
        'destination': 'Venice',
        'status': 'underway'
    },
    {
        'mmsi': '538008960',
        'vessel_name': 'NORTH TUG',
        'vessel_type': 'Tug',
        'flag_country': 'DK',
        'latitude': 56.0,
        'longitude': 12.0,
        'speed_over_ground': '4.5',
        'course_over_ground': '0.0',
        'heading': 2,
        'destination': 'Copenhagen',
        'status': 'at_anchor'
    },
]

for vessel_data in sample_vessels:
    vessel, created = Vessel.objects.get_or_create(
        mmsi=vessel_data['mmsi'],
        defaults={
            'vessel_name': vessel_data['vessel_name'],
            'vessel_type': vessel_data['vessel_type'],
            'flag_country': vessel_data['flag_country'],
            'latitude': vessel_data['latitude'],
            'longitude': vessel_data['longitude'],
            'speed_over_ground': vessel_data['speed_over_ground'],
            'course_over_ground': vessel_data['course_over_ground'],
            'heading': vessel_data['heading'],
            'destination': vessel_data['destination'],
            'status': vessel_data['status'],
            'is_tracked': True
        }
    )
    
    if created:
        print(f"✓ Created: {vessel_data['vessel_name']} (MMSI: {vessel_data['mmsi']})")
    else:
        print(f"  Already exists: {vessel_data['vessel_name']}")

print("\n✓ Sample vessels created!")
