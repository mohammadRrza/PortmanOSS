import sys
import os

sys.path.append('/opt/portmanv3/portman_web/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


from dslam.models import DSLAM
from dslam.models import DSLAMICMP
from dslam.models import DSLAMICMPSnapshot
from dslam.models import DSLAMEvent
