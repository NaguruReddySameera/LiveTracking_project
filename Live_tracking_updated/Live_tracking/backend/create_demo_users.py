#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime_project.settings')
django.setup()

from apps.authentication.models import User

demo_users = [
    {
        'email': 'sameerareddy583@gmail.com',
        'password': 'admin',
        'role': 'admin',
        'first_name': 'Admin',
        'last_name': 'User'
    },
    {
        'email': 'analyst@maritimetracking.com',
        'password': 'Analyst@123',
        'role': 'analyst',
        'first_name': 'Analyst',
        'last_name': 'User'
    },
    {
        'email': 'operator@maritimetracking.com',
        'password': 'Operator@123',
        'role': 'operator',
        'first_name': 'Operator',
        'last_name': 'User'
    }
]

for user_data in demo_users:
    user, created = User.objects.get_or_create(
        email=user_data['email'],
        defaults={
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'role': user_data['role'],
            'is_active': True,
            'is_verified': True,
            'is_staff': True if user_data['role'] == 'admin' else False
        }
    )
    
    # Always update password and ensure account is active
    user.set_password(user_data['password'])
    user.is_active = True
    user.is_verified = True
    user.role = user_data['role']
    if user_data['role'] == 'admin':
        user.is_staff = True
    user.save()
    
    if created:
        print(f"✓ Created {user_data['role'].upper()}: {user_data['email']}")
    else:
        print(f"✓ Updated {user_data['role'].upper()}: {user_data['email']}")

print("\n✓ Demo users setup complete!")
