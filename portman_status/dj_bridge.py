import sys
import os

sys.path.append('/opt/portmanv3/portman_web/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from dslam.models import DSLAM
from dslam.models import DSLAMPort
from dslam.models import DSLAMStatus
from dslam.models import DSLAMPortSnapshot
from dslam.models import DSLAMStatusSnapshot
from dslam.models import LineProfile
from dslam.models import DSLAMEvent
from dslam.models import DSLAMPortEvent
from dslam.models import DSLAMPortEvent
from dslam.models import Command
from dslam.models import PortCommand
from dslam.models import DSLAMCommand
from dslam.models import TelecomCenter
from dslam.models import DSLAMType
from dslam.models import City
from dslam.models import DSLAMBulkCommandResult
from dslam.models import DSLAMPortVlan
from dslam.models import Vlan
from dslam.models import DSLAMPortMac
from dslam.models import DSLAMBoard
from dslam.models import LineProfileExtraSettings
from dslam.models import DSLAMTypeCommand
