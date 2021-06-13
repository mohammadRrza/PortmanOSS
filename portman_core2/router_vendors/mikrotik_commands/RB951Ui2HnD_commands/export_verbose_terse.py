from netmiko import ConnectHandler
import sys, os
from .command_base import BaseCommand
import re


class ShowInventory(BaseCommand):
    def __init__(self, params):
        pass

    def run_command(self):
        try:
            device = ConnectHandler(device_type='extreme_vdx',
                                    ip='172.28.32.134',
                                    username='developer',
                                    password='developer')
            output = device.send_command("export verbose terse")
            return output

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return str(ex)
