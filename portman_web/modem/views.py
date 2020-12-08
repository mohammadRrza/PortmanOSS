import sys, os
from datetime import time
import kwargs as kwargs
from django.views.generic import View
from netmiko.cisco_base_connection import CiscoSSHConnection
from rest_framework import status, views, mixins, viewsets, permissions
from django.http import JsonResponse, HttpResponse
from netmiko import ConnectHandler
from netmiko.dlink.dlink_ds import DlinkDSTelnet, DlinkDSSSH
from netmiko.terminal_server.terminal_server import TerminalServerSSH


class GetModemInfoAPIView(views.APIView):
    def get_permissions(self):
        return (permissions.IsAuthenticated(),)

    def post(self, request, format=None):
        try:
            d_linkD = DlinkDSSSH(ip='46.209.102.8', username='admin', password='admin')
            s = d_linkD.check_enable_mode()
            return JsonResponse({'result': s})
        except Exception as ex:
         exc_type, exc_obj, exc_tb = sys.exc_info()
         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
         return JsonResponse({'result': 'Error is {0}'.format(ex), 'Line': str(exc_tb.tb_lineno)})


