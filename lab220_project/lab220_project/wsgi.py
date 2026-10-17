import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the project directory containing manage.py to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab220_project.settings')

application = get_wsgi_application()
app = application  # Required for Vercel Python runtime
