from dslam.models import DSLAM
from dslam import utility
from rest_framework import status
import re
from datetime import datetime


class GetPortTrafficService:
    def __init__(self, data, device_ip):
        self.data = data
        self.device_ip = device_ip

    def get_port_params(self):
        dslam_id = self.data.get('dslam_id')
        dslamObj = DSLAM.objects.get(pk=dslam_id)
        params = self.data.get('params', None)
        dslam_type = dslamObj.dslam_type_id

        try:
            result = utility.dslam_port_run_command(dslamObj.pk, 'get traffic', params)
            if result.get('status') == 200:
                return {'result': result['result'], 'status': status.HTTP_200_OK}
            else:
                return {'result': result, 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}
        except Exception as ex:
            return {'result': str(ex), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}
