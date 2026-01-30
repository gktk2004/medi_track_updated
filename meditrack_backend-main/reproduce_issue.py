
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meditrack.settings')
django.setup()

from django.test import Client
from meditrackapp.models import Doctor

def test_reschedule_page():
    print("Setting up test...")
    # Create or get a test doctor
    doctor, created = Doctor.objects.get_or_create(
        email='testdoctor@example.com',
        defaults={
            'name': 'Test Doctor', 
            'password': 'password',
            # Add other required fields if necessary, though defaults should handle usually
        }
    )
    if created:
        print(f"Created test doctor: {doctor.email}")
    else:
        print(f"Using existing test doctor: {doctor.email}")

    client = Client(SERVER_NAME='localhost')
    
    # Simulate login by setting session
    session = client.session
    session['doctor_id'] = doctor.id
    session['role'] = 'doctor'
    session.save()
    
    # Try to access the reschedule page
    url = '/meditrack/doctor/reschedule/request/'
    print(f"Testing URL: {url}")
    
    try:
        response = client.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Page loaded successfully.")
            # Check for specific content
            if "Request Token Reschedule" in response.content.decode():
                print("Found 'Request Token Reschedule' in content.")
            else:
                print("WARNING: 'Request Token Reschedule' NOT found in content.")
                print("First 500 chars of content:")
                print(response.content.decode()[:500])
        elif response.status_code == 302:
            print(f"Redirected to: {response.url}")
        else:
            print("Failed to load page.")
            
    except Exception as e:
        print(f"Exception during request: {e}")

if __name__ == "__main__":
    test_reschedule_page()
