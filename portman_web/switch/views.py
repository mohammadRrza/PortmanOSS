import sys, os
from datetime import time
from django.views.generic import View
from rest_framework import status, views, mixins, viewsets, permissions
from django.http import JsonResponse, HttpResponse
from rest_framework.permissions import IsAuthenticated
from switch.serializers import SwitchSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from switch.models import Switch
from netmiko import ConnectHandler
from switch import utility

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = max

class SwitchViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Switch.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = SwitchSerializer
    pagination_class = LargeResultsSetPagination

    def get_serializer(self, *args, **kwargs):
        if self.request.user.is_superuser:
            print(self.request.user.type)
            return SwitchSerializer(request=self.request, *args, **kwargs)
        elif self.request.user.type == 'SUPPORT':
            print(self.request.user.type)
            _fields = ['telnet_password', 'telnet_username', 'set_snmp_community', 'get_snmp_community', 'snmp_port']
            return SwitchSerializer(request=self.request, remove_fields=_fields, *args, **kwargs)
        else:
            print(self.request.user.type)
            _fields = ['telnet_password', 'telnet_username', 'set_snmp_community', 'get_snmp_community', 'snmp_port',
                       'ip', 'total_ports_count', 'down_ports_count', 'up_ports_count']
            return SwitchSerializer(request=self.request, remove_fields=_fields, *args, **kwargs)

    @action(methods=['GET'],detail=False)
    def current(self, request):
        serializer = SwitchSerializer(request.user, request=request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        sort_field = self.request.query_params.get('sort_field', None)
        switch_name = self.request.query_params.get('search_switch', None)
        device_ip = self.request.query_params.get('search_ip', None)
        ip_list = self.request.query_params.get('search_ip_list', None)
        city_id = self.request.query_params.get('search_city', None)
        telecom = self.request.query_params.get('search_telecom', None)
        active = self.request.query_params.get('search_active', None)
        status = self.request.query_params.get('search_status', None)
        switch_type_id = self.request.query_params.get('search_type', None)
        device_fqdn = self.request.query_params.get('search_fqdn', None)

        if switch_type_id:
            queryset = queryset.filter(switch_type__id=switch_type_id)

        if switch_name:
            queryset = queryset.filter(device_name__istartswith=switch_name)

        if device_ip:
            device_ip = device_ip.strip()
            if len(device_ip.split('.')) != 4:
                queryset = queryset.filter(device_ip__istartswith=device_ip)
            else:
                queryset = queryset.filter(device_ip=device_ip)
        if device_fqdn:
            queryset = queryset.filter(device_fqdn__icontains=device_fqdn)
        if ip_list:
            for ip in ip_list.split(','):
                queryset = queryset.filter(ip__istartswith=ip)

        if status:
            queryset = queryset.filter(status=status)

        if active:
            queryset = queryset.filter(active=bool(active))

        if city_id:
            city = City.objects.get(id=city_id)
            if city.parent is None:
                city_ids = City.objects.filter(parent=city).values_list('id', flat=True)
                telecom_ids = TelecomCenter.objects.filter(city__id__in=city_ids).values_list('id', flat=True)
            else:
                telecom_ids = TelecomCenter.objects.filter(city=city).values_list('id', flat=True)
            queryset = queryset.filter(telecom_center__id__in=telecom_ids)

        if telecom:
            telecom_obj = TelecomCenter.objects.get(id=telecom)
            queryset = queryset.filter(telecom_center=telecom_obj)

        if sort_field:
            if sort_field.replace('-', '') in ('telecom_center',):
                sort_field += '__name'
            elif sort_field.replace('-', '') in ('city',):
                sort_field = sort_field.replace('city', 'telecom_center__city__name')

            queryset = queryset.order_by(sort_field)

        return queryset

class ConnectHandlerTest(views.APIView):
    def get(self, request, format=None):
        try:
         result = utility.switch_run_command(410, 'show dot1x', None)
         return JsonResponse({'row': result})

         device = ConnectHandler(device_type='extreme_vdx', ip ='172.19.177.254', username = 'taherabadi', password = 't@h3r68')
         output = device.send_command("show dot1x")
         print(result)
         return JsonResponse({'row': output.split("\n")})

        except Exception as ex:
         exc_type, exc_obj, exc_tb = sys.exc_info()
         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
         return JsonResponse({'row': str(ex)})


