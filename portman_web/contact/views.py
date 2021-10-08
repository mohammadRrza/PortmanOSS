import sys, os
from datetime import time
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from rest_framework import status, views, mixins, viewsets, permissions
from contact.models import Order
from django.http import JsonResponse, HttpResponse
from rest_framework.permissions import IsAuthenticated
from contact.serializers import OrderSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action


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
    permission_classes = (IsAuthenticated, )
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

    @action(methods=['GET'],detail=False)
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