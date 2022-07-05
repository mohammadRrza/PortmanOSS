import os
import sys

from django.http import JsonResponse
from users.serializers import *
from users.models import PortmanLog


class PortmanLogging:

    def __init__(self, result, log_params):
        self.result = result
        self.log_params = log_params
        self.save_to_db()

    def prepare_variables(self, log_port_data, log_username, log_command, result,
                          log_date, log_ip, log_method_name, log_status,
                          log_reseller_name, log_exception_result):
        return dict(request=log_port_data, username=log_username, command=log_command, response=result,
                    log_date=log_date, source_ip=log_ip, method_name=log_method_name, status=log_status,
                    reseller_name=log_reseller_name, exception_result=log_exception_result)

    def save_to_db(self):
        try:
            PortmanLog.objects.create(request=self.log_params['request'],
                                      username=self.log_params['username'],
                                      command=self.log_params['command'],
                                      response=self.log_params['response'], log_date=self.log_params['log_date'],
                                      source_ip=self.log_params['source_ip'],
                                      method_name=self.log_params['method_name'],
                                      status=self.log_params['status'],
                                      exception_result=self.log_params['exception_result'],
                                      reseller_name=self.log_params['reseller_name'])
        except Exception as ex:
            print(ex)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return JsonResponse({'result': 'Error is {0}'.format(ex), 'Line': str(exc_tb.tb_lineno)})

