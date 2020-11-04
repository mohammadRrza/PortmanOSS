import sys
import os

sys.path.append('/opt/PortMan/portman_web/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from dslam.models import DSLAM
from dslam.models import DSLAMStatus
from dslam.models import DSLAMStatusSnapshot
from dslam.models import DSLAMEvent
