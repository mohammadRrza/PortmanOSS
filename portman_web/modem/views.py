import sys, os
from datetime import time
from django.views.generic import View
from rest_framework import status, views, mixins, viewsets, permissions
from django.http import JsonResponse, HttpResponse



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


