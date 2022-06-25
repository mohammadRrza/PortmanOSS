import json
import os
import sys

from celery import Celery

import utility
from dj_bridge import TelecomCenter, DSLAM


class port_condition:
    slot_number = 0
    port_number = 0


class param():
    command = ''
    type = ''
    is_queue = ''
    fqdn = ''
    dslam_number = 0
    slot_number = 0
    port_number = 0
    port_conditions = port_condition

def get_current_port_status():
    print('START')
    params = param()
    dslam_objs = DSLAM.objects.filter(fqdn='teh.tehn.atef.t.dsl.z6000.01')
    for dslam_obj in dslam_objs:
            telecom_center_id = DSLAM.objects.get(id=dslam_obj.id).telecom_center_id
            telecom_center = TelecomCenter.objects.get(id=telecom_center_id).name
            for i in range(1, 50):
                params = param()
                params.type = 'dslamport'
                params.is_queue = False
                params.fqdn = dslam_obj.fqdn
                params.port_conditions = port_condition()
                params.port_conditions.slot_number = '1'
                params.port_conditions.port_number = str(i)
                params = json.dumps(params, default=lambda x: x.__dict__)
                try:
                    result = utility.dslam_port_run_command(dslam_obj.pk, 'snmp get port params', json.loads(params))
                    print(result)
                    # return result
                except Exception as ex:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(ex, exc_tb.tb_lineno)
                    # return 'ERROR'
            print('OKKKKKKKK')



if __name__ == "__main__":
  res = get_current_port_status()

