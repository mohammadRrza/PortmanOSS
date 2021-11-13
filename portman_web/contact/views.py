import json
import sys, os
from datetime import time
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from rest_framework import status, views, mixins, viewsets, permissions
from contact.models import Order, Province
from django.http import JsonResponse, HttpResponse
from rest_framework.permissions import IsAuthenticated
from contact.serializers import OrderSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.core.serializers import serialize


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = max


class PortMapViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer
    pagination_class = LargeResultsSetPagination

    def get_serializer(self, *args, **kwargs):
        if self.request.user.is_superuser:
            print(self.request.user.type)
            return OrderSerializer(request=self.request, *args, **kwargs)
        elif self.request.user.type == 'SUPPORT':
            print(self.request.user.type)
            _fields = ['telnet_password', 'telnet_username', 'set_snmp_community', 'get_snmp_community', 'snmp_port']
            return OrderSerializer(request=self.request, remove_fields=_fields, *args, **kwargs)
        else:
            print(self.request.user.type)
            _fields = ['telnet_password', 'telnet_username', 'set_snmp_community', 'get_snmp_community', 'snmp_port',
                       'ip', 'total_ports_count', 'down_ports_count', 'up_ports_count']
            return OrderSerializer(request=self.request, remove_fields=_fields, *args, **kwargs)

    @action(methods=['GET'], detail=False)
    def current(self, request):
        serializer = OrderSerializer(request.user, request=request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        sort_field = self.request.query_params.get('sort_field', None)
        username = self.request.query_params.get('search_username', None)
        ranjePhoneNumber = self.request.query_params.get('search_ranjePhoneNumber', None)
        fqdn = self.request.query_params.get('search_ranjePhoneNumber', None)
        slot_number = self.request.query_params.get('search_slot_number', None)
        port_number = self.request.query_params.get('search_port_number', None)
        telco_row = self.request.query_params.get('search_telco_row', None)
        telco_Column = self.request.query_params.get('search_telco_Column', None)
        telco_connection = self.request.query_params.get('search_telco_connection', None)

        if username:
            queryset = queryset.filter(username__icontains=username)

        if ranjePhoneNumber:
            queryset = queryset.filter(ranjePhoneNumber__icontains=ranjePhoneNumber)

        if fqdn:
            queryset = queryset.filter(fqdn__icontains=fqdn)

        if slot_number:
            queryset = queryset.filter(slot_number=slot_number)

        if port_number:
            queryset = queryset.filter(port_number=port_number)

        if telco_row:
            queryset = queryset.filter(telco_row=telco_row)

        if telco_Column:
            queryset = queryset.filter(telco_Column=telco_Column)

        if telco_connection:
            queryset = queryset.filter(telco_connection=telco_connection)

        return queryset


class PortmapAPIView(views.APIView):

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def post(self, request, format=None):
        data = request.data
        queryset = Order.objects.all()

        username = data.get('username', None)
        province_name = data.get('province_name', None)
        city_name = data.get('city_name', None)
        telecom_name = data.get('telecom_name', None)
        status = data.get('status', None)
        port_owner = data.get('port_owner', None)
        port_type = data.get('port_type', None)
        search_type = data.get('search_type', None)
        from_row = data.get('from_row', 1)
        to_row = data.get('to_row', 1000)
        from_dslam = data.get('from_dslam', 1)
        to_dslam = data.get('to_dslam', 3)
        from_floor = data.get('from_floor', 1)
        to_floor = data.get('to_floor', 15)
        from_card = data.get('from_card', 1)
        to_card = data.get('to_card', 80)
        from_connection = data.get('from_connection', '1')
        to_connection = data.get('to_connection', '100')
        from_port = data.get('from_port', 1)
        to_port = data.get('to_port', 100)
        prefix_num = data.get('prefix_num', None)
        ranje_num = data.get('ranje_num', None)
        show_deleted = data.get('show_deleted', None)
        show_priorities = data.get('show_priorities', None)

        try:
            if province_name:
                queryset = queryset.filter(province_name__icontains=province_name)
            if city_name:
                queryset = queryset.filter(city_name__icontains=city_name)
            if telecom_name:
                queryset = queryset.filter(telecom_name__icontains=telecom_name)
            if status:
                queryset = queryset.filter(status=status)
            if port_owner:
                queryset = queryset.filter(port_owner__icontains=port_owner)
            if port_type:
                queryset = queryset.filter(port_type=port_type)
            if search_type == "bukht":
                queryset = queryset.filter(Q(telco_row__gte=from_row) & Q(telco_row__lte=to_row)).filter(
                    Q(telco_column__gte=from_row) & Q(telco_column__lte=to_row)).filter(
                    Q(telco_connection__gte=from_connection) & Q(telco_connection__lte=to_connection))
            if search_type == "port":
                queryset = queryset.filter(Q(from_row__gte=from_dslam) & Q(to_row__lte=to_dslam)).filter(
                    Q(from_row__gte=from_card) & Q(to_row__lte=to_card)).filter(
                    Q(from_row__gte=from_port) & Q(to_row__lte=to_port))
            if prefix_num:
                queryset = queryset.filter(prefix_num__icontains=prefix_num)
            if ranje_num:
                queryset = queryset.filter(ranje_num__icontains=ranje_num)
            if show_deleted:
                queryset = queryset.filter(show_deleted=show_deleted)
            if show_priorities:
                queryset = queryset.filter(show_priorities=show_priorities)
            result = serialize('json', queryset)
            return HttpResponse(result, content_type='application/json')

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return JsonResponse({'row': str(ex) + '////' + str(exc_tb.tb_lineno)})


class GetProvincesAPIView(views.APIView):
    def get(self, request, format=None):
        try:
            province_name = request.query_params.get('province_name')
            if province_name:
                provinces = Province.objects.filter(provinceName__icontains=province_name).values().order_by('provinceName')[:10]
                return JsonResponse({"result": list(provinces)})
            provinces = Province.objects.all().values().order_by('provinceName')[:10]
            return JsonResponse({"result": list(provinces)})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})
