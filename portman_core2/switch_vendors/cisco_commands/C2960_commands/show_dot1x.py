from netmiko import ConnectHandler
import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class ShowDot1x(BaseCommand):
    def __init__(self):
        pass

    def run_command(self):
        try:
            device = ConnectHandler(device_type='extreme_vdx', ip='172.19.177.254', username='taherabadi',
                                    password='t@h3r68')
            output = device.send_command("show dot1x")
            print(output)
            return JsonResponse({'row': output.split("\n")})

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return JsonResponse({'row': str(ex)})
