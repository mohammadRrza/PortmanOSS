from netmiko import ConnectHandler
import sys, os
from .command_base import BaseCommand
import re


class ExportVerboseTerse(BaseCommand):
    def __init__(self, params):
        pass

    def run_command(self):
        try:
            device = {
                'device_type': 'mikrotik_routeros',
                'host': '172.28.32.134',
                'username': 'admin',
                'password': '4dFjjrSKqx2WsXfu',
                'port': 22
            }
            connection = ConnectHandler(**device)
            output = connection.send_command('export verbose terse')
            return output

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return str(ex) + "  // " + str(exc_tb.tb_lineno)
