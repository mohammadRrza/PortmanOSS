import sys
import os

sys.path.append('/opt/portmanv3/portman_web/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from dslam.models import DSLAM
from dslam.models import DSLAMPort
from dslam.models import DSLAMPortVlan
from dslam.models import DSLAMPortMac
from dslam.models import Vlan
