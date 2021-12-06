from users.serializers import *
from users.models import PortmanLog


class PortmanLogging:

    def __init__(self, request, username, command, response, log_date, source_ip, method_name, status,
                 exception_result):
        self.request = request
        self.username = username
        self.command = command
        self.response = response
        self.log_date = log_date
        self.source_ip = source_ip
        self.method_name = method_name
        self.status = status
        self.exception_result = exception_result

    def save_to_db(self):
        return PortmanLog.objects.create(request=self.request, username=self.username, command=self.command,
                                         response=self.response,
                                         log_date=self.log_date, source_ip=self.source_ip, method_name=self.method_name,
                                         status=self.status,
                                         exception_result=self.exception_result)


