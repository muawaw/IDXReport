import sys
import os

# Define the repository root path
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Add the repository root and backend directory to the Python path
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, 'apps', 'backend'))

# Set the Django settings module matching your folder structure
os.environ['DJANGO_SETTINGS_MODULE'] = 'django.core.settings'

# Initialize the WSGI application for Phusion Passenger
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()