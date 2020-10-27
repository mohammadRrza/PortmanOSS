from django.shortcuts import render
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.db import connection
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from datetime import date, timedelta, datetime
from django.db.models import Count
from django.core.serializers import serialize
from django.db.models import Value
from django.db.models.functions import Concat
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.postgres.search import SearchVector
from django.http import StreamingHttpResponse
import re
import requests
from rest_framework.response import Response
from rest_framework import status, views, mixins, viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import detail_route, list_route

from users.permissions.dslam_permission import DSLAMView, DSLAMEdit
from users.permissions.dslamport_permission import DSLAMPortView, DSLAMPortEdit
from users.permissions.command_permission import CommandView, CommandEdit
from users.permissions.telecom_center_permission import TelecomCenterView, TelecomCenterEdit

from khayyam import JalaliDatetime
import csv, time
import simplejson as json
import cStringIO as StringIO
from collections import defaultdict
import utility
import logging
import sys, os

from dslam.models import DSLAM, TelecomCenter, DSLAMPort, DSLAMPortSnapshot, LineProfile, TelecomCenterLocation, Vlan, DSLAMBulkCommandResult, \
    TelecomCenterMDF, DSLAMEvent, DSLAMPortEvent, Reseller, ResellerPort, CustomerPort, DSLAMLocation, DSLAMICMPSnapshot, DSLAMICMP, \
    PortCommand, ResellerPort, City, Command, DSLAMType, Terminal, DSLAMStatusSnapshot, DSLAMStatus, DSLAMCommand, CityLocation, MDFDSLAM, DSLAMPortVlan,\
    DSLAMPortMac, DSLAMBoard, DSLAMFaultyConfig, DSLAMPortFaulty,DSLAMTypeCommand, DSLAMCart
from dslam.permissions import HasAccessToDslam, IsAdminUser, HasAccessToDslamPort, \
    HasAccessToDslamPortSnapshot
from dslam.serializers import *
from users.helpers import add_audit_log


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = max


class VlanViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = VlanSerializer
    queryset = Vlan.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        reseller_id = self.request.query_params.get('reseller_id', None)
        reseller_name = self.request.query_params.get('reseller_name', None)
        dslam_id = self.request.query_params.get('dslam_id', None)
        vlan_name = self.request.query_params.get('vlan_name', None)
        vlan_id = self.request.query_params.get('vlan_id', None)
        sort_field = self.request.query_params.get('sort_field',None)

        if reseller_id:
            queryset = queryset.filter(reseller__id=reseller_id)

        if reseller_name:
            resellers = Reseller.objects.filter(name__istartswith=reseller_name)
            queryset = queryset.filter(reseller__in=resellers)

        if vlan_name:
            queryset = queryset.filter(vlan_name__istartswith=vlan_name)

        if vlan_id:
            queryset = queryset.filter(vlan_id=vlan_id)

        if dslam_id:
            port_ids = DSLAMPort.objects.filter(dslam__id=dslam_id).values_list('id', flat=True)
            vlan_obj_ids = DSLAMPortVlan.objects.filter(port__id__in=port_ids).values_list('vlan__vlan_id', flat=True)
            queryset = queryset.filter(vlan_id__in=vlan_obj_ids)

        if sort_field:
            queryset = queryset.order_by(sort_field)

        return queryset

    def create(self, request, *args, **kwargs):
        self.user = request.user
        data = request.data
        vlan_name = data.get('vlan_name')
        if not vlan_name:
            data['vlan_name'] = data.get('vlan_id')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        description = u'ADD Vlan {0}'.format(serializer.data['vlan_id'])
        add_audit_log(request, 'Vlan', serializer.data['id'], 'Create Vlan', description)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @list_route(methods=['POST'])
    def assign_to_reseller(self, request):
        user = request.user
        data = request.data
        reseller_id = data.get('reseller_id')
        vlan_id = data.get('vlan_id')
        if reseller_id:
            identifier_keys = ResellerPort.objects.filter(reseller__id=reseller_id).values_list('identifier_key', flat=True)
            dslam_ids = MDFDSLAM.objects.filter(identifier_key__in=identifier_keys).values_list('dslam_id', flat=True).distinct()

        params = {
                "is_queue": False,
                "type": "dslam",
                "vlan_id": vlan_id,
                "vlan_name": data.get('vlan_name', vlan_id),
                "username": user.username
                }

        for dslam_id in dslam_ids:
            if params.get('vlan_id'):
                result = utility.dslam_port_run_command(mdf_dslam_obj.dslam_id, 'create vlan', params)

        reseller = Reseller.objects.get(id=reseller_id)
        vlan = Vlan.objects.get(vlan_id=vlan_id)
        vlan.reseller=reseller
        vlan.save()
        serializer = self.get_serializer(vlan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response(data={
        #    'id': vlan.id,
        #    'vlan_id': vlan.vlan_id,
        #    'vlan_name': vlan.vlan_name,
        #    'reseller': reseller.id
        #    }, status=status.HTTP_201_CREATED, headers=headers)


    @list_route(methods=['POST'])
    def assign_to_subscibers(self, request):
        data = request.data
        user = request.user
        new_vlan_id = data.get('new_vlan_id')
        vlan_obj = Vlan.objects.get(vlan_id=new_vlan_id)
        reseller_vlan = data.get('reseller_vlan')
        identifier_key = data.get('identifier_key')
        card_ports = data.get('card_port')

        dslam_ports = defaultdict(list)
        print('*************************************************')
        print(data)
        if reseller_vlan:
            flag = reseller_vlan.get('flag')
            reseller_id = reseller_vlan.get('reseller_id')
            mdf_ports = None

            if not flag:
                return Response({'result': 'please send flag item.'}, status=status.HTTP_400_BAD_REQUEST)

            identifier_keys = ResellerPort.objects.filter(reseller__id=reseller_id).values_list('identifier_key', flat=True)

            if flag == 'all':
                mdf_ports = MDFDSLAM.objects.filter(identifier_key__in=identifier_key).values('dslam_id', 'slot_number', 'port_number')
                for mdf_port in mdf_ports:
                    try:
                        port = DSLAMPort.objects.get(
                                dslam__id=mdf_port.get('dslam_id'),
                                slot_number=mdf_port.get('slot_number'),
                                port_number=mdf_port.get('port_number')).values('id', 'slot_number', 'port_number', 'port_index')
                        dslam_ports[mdf_port.get('dslam_id')].append(port)
                    except:
                        pass

            elif flag == 'vlan':
                vlan_id = Vlan.objects.get(vlan_id=reseller_vlan.get('vlan_id')).vlan_id
                ports = DSLAMPortVlan.objects.filter(vlan__vlan_id=vlan_id).values('port__id', 'port__dslam_id', 'port__slot_number', 'port__port_number', 'port__port_index')
                for port in ports:
                    dslam_ports[port.get('port__dslam_id')].append({
                        'port_number': port.get('port__port_number'),
                        'slot_number': port.get('port__slot_number'),
                        'port_index': port.get('port__port_index'),
                        'id': port.get('port__id')
                        })

            elif flag == 'no-vlan':
                identifier_keys = ResellerPort.objects.filter(reseller__id=reseller_id).values_list('identifier_key', flat=True)
                mdf_ports = set(MDFDSLAM.objects.filter(identifier_key__in=identifier_key).values_list('dslam_id', 'slot_number', 'port_number'))
                vlan_obj_ids = Vlan.objects.filter(reseller__id=reseller_id).values_list('vlan__id', flat=True)
                ports = set(DSLAMPortVlan.objects.filter(vlan__id__in=vlan_obj__ids).values_list('port__dslam_id', 'port__slot_number', 'port__port_number'))
                reseller_ports_no_vlan = ports - mdf_ports

                for dslam_id, slot_number, port_index in reseller_ports_no_vlan:
                    try:
                        port = DSLAMPort.objects.get(
                                dslam__id=dslam_id,
                                slot_number=slot_number,
                                port_number=port_number).values('id', 'slot_number', 'port_number', 'port_index')
                        dslam_ports[dslam_id].append(port)
                    except:
                        pass


        elif identifier_key:
            mdf_ports = MDFDSLAM.objects.filter(identifier_key=identifier_key).values('dslam_id', 'slot_number', 'port_number')
            for mdf_port in mdf_ports:
                try:
                    port = DSLAMPort.objects.get(
                            dslam__id=mdf_port.get('dslam_id'),
                            slot_number=mdf_port.get('slot_number'),
                            port_number=mdf_port.get('port_number')).values('id', 'slot_number', 'port_number', 'port_index')
                    dslam_ports[mdf_port.get('dslam_id')].append(port)
                except:
                    pass

        elif card_ports:
            print '-------++====++++------------------------------------'
            print card_ports
            print '-------------------------------------------'
            port = DSLAMPort.objects.get(
                    dslam__id=card_ports.get('dslam_id'),
                    slot_number=card_ports.get('slot_number'),
                    port_number=card_ports.get('port_number'))
            dslam_ports[card_ports.get('dslam_id')].append({
                'id': port.id,
                'slot_number': port.slot_number,
                'port_number': port.port_number})

        if len(dslam_ports) > 0:
            for dslam_id ,port_indexes in dslam_ports.iteritems():
                params = {
                    "is_queue": False,
                    "type": "dslam",
                    "dslam_id": dslam_id,
                    "vlan_id": vlan_obj.vlan_id,
                    "vlan_name": vlan_obj.vlan_name,
                    "username": user.username
                    }
                result = utility.dslam_port_run_command(dslam_id, 'create vlan', params)
                print ('////////////////////////////////////////////////////////')
                params = {
                        "type":"dslamport",
                        "is_queue":False,
                        "vlan_id": vlan_obj.vlan_id,
                        "vlan_name": vlan_obj.vlan_name,
                        "dslam_id": dslam_id,
                        "port_indexes": port_indexes,
                        "username": user.username
                        }
                result = utility.dslam_port_run_command(dslam_id, 'add to vlan', params)
                for port in port_indexes:
                    print port.get('id')
                    port_vlan = DSLAMPortVlan.objects.get(port__id=port.get('id'))
                    port_vlan.vlan = vlan_obj
                    port_vlan.save()
            print ('-=-=-=-=-=-=-=-=-=')

            return Response({'result': 'vlans assign to subscribers'}, status=status.HTTP_201_CREATED)
        else:
            print ('afsfsfafsdfgawsfgsadgfasdgfadgfbadfkgjadpidbgjiadfgoiuo')
            return Response({'error': 'port does not existed!'}, status=status.HTTP_400_BAD_REQUEST)



    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        data = request.data
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if data.get('params') and data.get('dslam_id'):
            params['username'] = request.user.username
            result = utility.dslam_port_run_command(dslam_obj.pk, 'create vlan', params)
        self.perform_update(serializer)
        description = u'Update Vlan {0}: {1}'.format(instance.vlan_name, request.data)
        add_audit_log(request, 'Vlan', instance.id, 'Update Vlan', description)
        return Response(serializer.data)


    def destroy(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        self.perform_destroy(instance)
        description = u'Delete vlan {0}'.format(instance.vlan_id)
        add_audit_log(request, 'Vlan', instance.id, 'Delete Vlan', description)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DSLAMPortVlanViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = DSLAMPortVlanSerializer
    queryset = DSLAMPortVlan.objects.all()

    def get_queryset(self):
        dslamport_id = self.request.query_params.get('dslamport_id', None)
        sort_field = self.request.query_params.get('sort_field',None)
        queryset = self.queryset

        if dslamport_id:
            queryset = queryset.filter(port__id=dslamport_id)

        if sort_field:
            queryset = queryset.order_by(sort_field)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        if data.get('params') and data.get('dslam_id'):
            result = utility.dslam_port_run_command(data.get('dslam_id'), 'add to vlan', data.get('params'))

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        description = u'ADD port {0} to Vlan {1}'.format(serializer.data['vlan_id'], data.get('params'))
        add_audit_log(request, 'DSLAMPortVlan', serializer.data['id'], 'Add port to vlan', description)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def destroy(self, request, *args, **kwargs):
        data = request.data
        if data.get('dslam_id') and data.get('params'):
            result = utility.dslam_port_run_command(dslam_obj.pk, 'delete from vlan', params)
        instance = self.get_object()
        self.perform_destroy(instance)
        description = u'Delete DSLAMPortVlan {0}: {1}'.format(instance.name, request.data)
        add_audit_log(request, 'DSLAMPortVlan', instance.id, 'Delete DSLAMPortVlan', description)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        data = request.data
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if data.get('params') and data.get('dslam_id'):
            result = utility.dslam_port_run_command(dslam_obj.pk, 'add to vlan', params)
        self.perform_update(serializer)
        description = u'Update DSLAMPortVlan {0}: {1}'.format(instance.name, request.data)
        add_audit_log(request, 'DSLAMPortVlan', instance.id, 'Update DSLAMPort Vlan', description)
        return Response(serializer.data)


class TerminalViewSet(mixins.ListModelMixin,
        viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, HasAccessToDslam)
    serializer_class = TerminalSerializer
    queryset = Terminal.objects.all()
    paginate_by = None
    paginate_by_param = None
    paginator = None


class LineProfileViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, HasAccessToDslam)
    serializer_class = LineProfileSerializer

    @list_route(methods=['POST'])
    def assign_to_port(self, request):
        user = request.user
        data = request.data
        params = data.get('params')
        result = utility.dslam_port_run_command(dslam_id, 'change lineprofile port', params)
        if 'error' not in result['result']:
            dslamport = DSLAMPort.objects.get(dslam__id=dslam_id, slot_number=slot_number, port_number=port_number)
            serializer = DSLAMPortSerializer(dslamport)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


    def get_queryset(self):
        queryset = LineProfile.objects.all()
        profile_name = self.request.query_params.get('profile_name', None)
        sort_field = self.request.query_params.get('sort_field',None)

        if profile_name:
            queryset = queryset.filter(name__istartswith=profile_name)

        if sort_field:
            queryset = queryset.order_by(sort_field)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        extra_settings = data.get('extra_settings_info')
        lst_profile_settings = []

        for setting in extra_settings:
            if setting.get('value'):
                lst_profile_settings.append(setting)

        if bool(lst_profile_settings):
            line_profile = LineProfile.objects.get(id=serializer.data.get('id'))
            for setting in lst_profile_settings:
                lineprofile_settings = LineProfileExtraSettings()
                lineprofile_settings.line_profile = line_profile
                lineprofile_settings.attr_name = setting.get('key')
                lineprofile_settings.attr_value = setting.get('value')
                lineprofile_settings.save()
        description = u'Create LineProfile : {0}'.format(serializer.data['name'])
        add_audit_log(request, 'LineProfile', serializer.data['id'], 'Create LineProfile', description)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        description = u'Delete LineProfile : {0}'.format(instance.name)
        add_audit_log(request, 'LineProfile', instance.id, 'Delete LineProfile', description)
        return Response(status=status.HTTP_204_NO_CONTENT)

    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        description = u'Delete LineProfile : {0}'.format(instance.name)
        add_audit_log(request, 'LineProfile', serializer.data['id'], 'Update LineProfile', description)
        return Response(serializer.data)

class TelecomCenterMDFViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    paginate_by = None
    paginate_by_param = None
    paginator = None
    permission_classes = (IsAuthenticated, )
    serializer_class = TelecomCenterMDFSerializer

    def get_queryset(self):
        queryset = TelecomCenterMDF.objects.all().order_by('priority')
        telecom_id = self.request.query_params.get('telecom_id',None)
        sort_field = self.request.query_params.get('sort_field',None)

        if telecom_id:
            queryset = queryset.filter(telecom_center__id=telecom_id)

        if sort_field:
            queryset = queryset.order_by(sort_field)

        return queryset


    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        description = u'Create Telecom Center MDF: {0}'.format(serializer.data.get('name'))
        add_audit_log(request, 'TelecomCenterMDF', serializer.data['id'], 'Create Telecome Center MDF', description)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        description = u'Update Telecom Center MDF {0}: {1}'.format(instance.id, request.data)
        add_audit_log(request, 'TelecomCenterMDF', instance.id, 'Update Telecom Center MDF', description)
        return Response(serializer.data)


    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        description = u'Delete Telecom Center MDF: {0}'.format(instance.id)
        add_audit_log(request, 'TelecomCenterMDF', instance.id, 'Delete Telecom Center MDF', description)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DSLAMViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    queryset = DSLAM.objects.all()
    permission_classes = (IsAuthenticated, DSLAMView, DSLAMEdit)
    serializer_class = DSLAMSerializer
    pagination_class = LargeResultsSetPagination

    def get_serializer(self, *args, **kwargs):
        #if self.request.user.is_superuser or self.request.user.has_permission('edit_dslam'):
        if self.request.user.is_superuser:
            print (self.request.user.type)
            return DSLAMSerializer(request=self.request, *args, **kwargs)
        elif self.request.user.type == 'SUPPORT':
            print (self.request.user.type)
            _fields = ['telnet_password', 'telnet_username', 'set_snmp_community', 'get_snmp_community', 'snmp_port']
            return DSLAMSerializer(request=self.request, remove_fields=_fields, *args, **kwargs)
        else:
            print (self.request.user.type)
            _fields = ['telnet_password', 'telnet_username', 'set_snmp_community', 'get_snmp_community', 'snmp_port', 'ip', 'total_ports_count', 'down_ports_count', 'up_ports_count']
            return DSLAMSerializer(request=self.request, remove_fields=_fields, *args, **kwargs)

    @list_route(methods=['GET'])
    def current(self, request):
        serializer = DSLAMSerializer(request.user, request=request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        sort_field = self.request.query_params.get('sort_field',None)
        dslam_name = self.request.query_params.get('search_dslam',None)
        ip = self.request.query_params.get('search_ip',None)
        ip_list = self.request.query_params.get('search_ip_list',None)
        city_id = self.request.query_params.get('search_city',None)
        telecom = self.request.query_params.get('search_telecom',None)
        active = self.request.query_params.get('search_active',None)
        status = self.request.query_params.get('search_status',None)
        dslam_type_id = self.request.query_params.get('search_type',None)

        if dslam_type_id:
            queryset = queryset.filter(dslam_type__id=dslam_type_id)

        if dslam_name :
            queryset = queryset.filter(name__istartswith=dslam_name)

        if ip:
            if len(ip.split('.')) != 4:
                queryset = queryset.filter(ip__istartswith=ip)
            else:
                queryset = queryset.filter(ip=ip)


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

        if sort_field :
            if sort_field.replace('-', '') in ('telecom_center', ):
                sort_field += '__name'
            elif sort_field.replace('-', '') in ('city', ):
                sort_field = sort_field.replace('city', 'telecom_center__city__name')

            queryset = queryset.order_by(sort_field)

        return queryset


    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, request=request)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        description = u'Add DSLAM {0}'.format(serializer.data['name'])
        add_audit_log(request, 'DSLAM',serializer.data['id'], 'Add DSLAM', description)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, request=self.request, partial = partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        description = u'Update DSLAM {0}: {1}'.format(instance.name, request.data)
        add_audit_log(request, 'DSLAM', instance.id, 'Update DSLAM', description)
        return Response(serializer.data)


    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        description = u'Delete DSLAM {0}'.format(instance.name)
        add_audit_log(request, 'DSLAM', instance.id, 'Delete DSLAM', description)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['GET'])
    def get_dslam_names(self, request):
        data = request.query_params
        exclude_dslam_ids = data.get('exclude_dslam_id')
        dslam_name = data.get('dslam_name')
        dslams = DSLAM.objects.all()
        if dslam_name:
            dslams = dslams.filter(name__istartswith=dslam_name)

        if exclude_dslam_ids:
            exclude_dslam_ids = eval(exclude_dslam_ids)
            dslams = dslams.exclude(id__in=exclude_dslam_ids)


        return Response({'result':dslams.annotate(search_name=Concat('ip', Value(' - '), 'name')).values('id', 'search_name', 'name')})


    @detail_route(methods=['GET',])
    def getvlan(self, request, pk=None):
        user = request.user
        data = self.request.query_params
        dslam_id = self.get_object().id
        if not dslam_id:
            return Response({'result': 'dslam_id does not exists'}, status=status.HTTP_400_BAD_REQUEST)
        vlan_obj_ids = DSLAMPortVlan.objects.filter(port__dslam__id=dslam_id).values_list('vlan', flat=True).distinct()
        vlans_json = json.dumps([dict(item) for item in Vlan.objects.filter(id__in=vlan_obj_ids).values('id', 'vlan_id', 'vlan_name', 'reseller')])
        return JsonResponse(
                {'vlans': vlans_json})


    @detail_route(methods=['GET',])
    def vlan_usage_percentage(self, request, pk=None):
        user = request.user
        data = self.request.query_params
        dslam = self.get_object()
        if not dslam:
            return Response({'result': 'dslam_id does not exists'}, status=status.HTTP_400_BAD_REQUEST)
        result = utility.dslam_port_run_command(dslam.id, 'vlan show', {"is_queue": False,"type": "dslam"})
        if bool(result):
            all_vlan_count = {key:{'vlan_name': value, 'total': 0, 'percentage': 0.0} for key,value in result['result'].iteritems()}
            ports = DSLAMPort.objects.filter(dslam=dslam)
            vlans_count = DSLAMPortVlan.objects.filter(port__in=ports).values('vlan__vlan_id','vlan__vlan_name','vlan').annotate(total=Count('vlan')).order_by('total')
            sum_vlan_count = sum([int(item['total']) for item in vlans_count])
            for vlan_count in vlans_count:
                all_vlan_count[str(vlan_count['vlan__vlan_id'])]['total'] = vlan_count['total']
                all_vlan_count[str(vlan_count['vlan__vlan_id'])]['id'] = vlan_count['vlan']
                all_vlan_count[str(vlan_count['vlan__vlan_id'])]['percentage'] = float(vlan_count['total'])/sum_vlan_count*100
            return JsonResponse({'values': all_vlan_count})
        return JsonResponse(
                    {'values': []})

    @detail_route(methods=['GET'])
    def scan(self,request, pk=None):
        dslam_id = self.get_object().id
        scan_type = self.request.query_params.get('type',None)
        if scan_type == 'port':
            result = utility.scan_dslamport(dslam_id)
        elif scan_type == 'general':
            result = utility.scan_dslam_general_info(dslam_id)
        if 'error' not in result:
            return JsonResponse({'values': 'dslam ready to updating'})
        return JsonResponse({'values': 'error when dslam updating'})

    @list_route(methods=['GET'])
    def count(self, request):
        dslam_count = DSLAM.objects.all().count()
        return Response({'dslam_count':dslam_count})

    @detail_route(methods=['GET'])
    def dslamreport(self, request, pk=None):
        dslam_obj = self.get_object()
        dslam_info = dslam_obj.get_info()
        queryset = DSLAMPort.objects.filter(dslam=dslam_obj)
        total_ports = queryset.count()
        up_ports = queryset.filter(admin_status='UNLOCK').count()
        down_ports = queryset.filter(admin_status='LOCK').count()
        sync_ports = queryset.filter(oper_status='SYNC').count()
        nosync_ports = queryset.filter(oper_status='NO-SYNC').count()

        line_profile_usage = DSLAMPort.objects.filter(dslam=dslam_obj).values(
            'line_profile'
        ).annotate(
            usage_count=Count('line_profile')
        )

        line_profile_usage = [{'name':item['line_profile'], 'y':item['usage_count']} for item in line_profile_usage]

        dslam_info['updated_at'] = str(JalaliDatetime(dslam_info['updated_at']).strftime("%Y-%m-%d %H:%M:%S"))
        dslam_info['created_at'] = str(JalaliDatetime(dslam_info['created_at']).strftime("%Y-%m-%d %H:%M:%S"))
        #dslam_info['last_sync'] = str(JalaliDatetime(dslam_info['last_sync']).strftime("%Y-%m-%d %H:%M:%S"))

        return JsonResponse({\
                'dslam': dslam_info, 'total_ports':total_ports,\
                'up_ports':up_ports, 'down_ports':down_ports, 'sync_ports':sync_ports,\
                'dslam_type':dslam_obj.dslam_type.name,'nosync_ports':nosync_ports, \
                'line_profile_usage':json.dumps(line_profile_usage), \
                'dslam_availability': dslam_obj.get_dslam_availability}
        )

    @detail_route(methods=['GET'])
    def dslam_curr_temperature_report(self, request, pk=None):
        user = request.user
        dslam = self.get_object()
        if not dslam:
            return Response({'result': 'Invalid DSLAM'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dslamstatus = DSLAMStatus.objects.get(dslam=dslam)
        except Exception as e:
            print e
            return Response({'result': str(e)}, status=status.HTTP_400_BAD_REQUEST)


        lst_line_cards = []
        lst_line_card_values = []
        for obj_card_temp in dslamstatus.line_card_temp:
                lst_line_cards.append(obj_card_temp['name'])
                lst_line_card_values.append(int(obj_card_temp['CurValue']))
        return JsonResponse({'names':lst_line_cards,'values':lst_line_card_values})

    @detail_route(methods=['GET'])
    def dslam_range_temperature_report(self, request, pk=None):
        user = request.user
        dslam = self.get_object()
        lc_name = self.request.query_params.get('lc_name',None)
        if not lc_name:
            # LC1-TEMP1
            card_number = self.request.query_params.get('card_number',None)
            temp_name = self.request.query_params.get('temp_name',None)
            lc_name = 'LC{0}-{1}'.format(card_number, temp_name.upper())
        start_date = self.request.query_params.get('start_date',None)
        end_date = self.request.query_params.get('end_date',None)
        if not dslam:
            return Response({'result': 'Invalid DSLAM'}, status=status.HTTP_400_BAD_REQUEST)
        #try:
        if start_date:
            #for example start_date = 20120505 and end_date = 20120606
            start_date = datetime.strptime(start_date[0:4]+'-'+start_date[4:6]+'-'+start_date[6:8], '%Y-%m-%d').date()
            if end_date:
                end_date = datetime.strptime(end_date[0:4]+'-'+end_date[4:6]+'-'+end_date[6:8], '%Y-%m-%d').date()
            else:
                end_date = date.today()

            dslamstatus_snapshots = DSLAMStatusSnapshot.objects.filter(
                dslam_id=dslam.id
            ).filter(created_at__gte=start_date,created_at__lt=end_date).order_by('created_at')

        else:
            now = datetime.now()
            DD = timedelta(days=7)
            date_from = now - DD
            dslamstatus_snapshots = DSLAMStatusSnapshot.objects.filter(
                dslam_id=dslam.id
            ).filter(created_at__gte=date_from).order_by('created_at')

        lst_datetimes = []
        lst_line_card_values = []
        for obj in dslamstatus_snapshots:
            for card_temp in obj.line_card_temp:
                if isinstance(card_temp,dict):
                    if card_temp['name'] == lc_name:
                        lst_datetimes.append(JalaliDatetime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S"))
                        lst_line_card_values.append(int(card_temp['CurValue']))
        return JsonResponse({'names':lst_datetimes,'values':lst_line_card_values})


    @list_route(methods=['GET'])
    def dslam_range_ping_report(self, request):
        user = request.user
        dslam_id = self.request.query_params.get('dslam_id',None)
        start_date = self.request.query_params.get('start_date',None)
        end_date = self.request.query_params.get('end_date',None)
        identifier_key = self.request.query_params.get('identifier_key',None)
        username = self.request.query_params.get('username',None)

        if username:
            identifier_key = CustomerPort.objects.get(username=username).identifier_key

        if identifier_key:
            dslam_id = MDFDSLAM.objects.filter(identifier_key=identifier_key)[0].dslam_id

        if dslam_id:
            dslam = DSLAM.objects.get(id=dslam_id)
        else:
            return Response({'result': 'please send dslam_id '}, status=status.HTTP_400_BAD_REQUEST)


        if start_date:
            pass
        else:
            now = datetime.now()
            DD = timedelta(days=14)
            date_from = now - DD
            try:
                dslam_icmp_snapshots = DSLAMICMPSnapshot.objects.filter(
                    dslam_id=dslam.id
                ).filter(created_at__gte=date_from).order_by('created_at')


            except Exception as e:
                print e
                return Response({'result': 'Dont Still Add This DSLAM For Getting ICMP'}, status=status.HTTP_400_BAD_REQUEST)

        lst_datetimes = []
        lst_avgping_values = []
        dslamicmp_values = {}
        try:
            for obj in dslam_icmp_snapshots:
                if obj.avgping == 'NaN' or obj.avgping is None:
                    continue
                persian_date = JalaliDatetime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")
                lst_datetimes.append(persian_date)
                lst_avgping_values.append(float(obj.avgping))
                icmp_values = {
                        'avgping': obj.avgping,
                        'jitter': obj.jitter,
                        'maxping': obj.maxping,
                        'minping': obj.minping,
                        'packet_loss': obj.packet_loss,
                        'received': obj.received,
                        'sent': obj.sent,
                        }
                dslamicmp_values[persian_date] = icmp_values
        except:
            print 'give error dslam icmp : \n{0} - type is {1}'.format(obj.avgping, type(obj.avgping))

        return JsonResponse({'names':lst_datetimes,'values':lst_avgping_values, 'dslamicmp_values': dslamicmp_values}, safe=False)

    @detail_route(methods=['GET'])
    def dslam_icmp_info(self,request, pk=None):
        user = request.user
        dslam= self.get_object()
        date = self.request.query_params.get('date',None)
        if date:
            date_start = JalaliDatetime.strptime(date, '%Y-%m-%d %H:%M:%S').todatetime()
            DD = timedelta(seconds=1)
            date_end = date_start + DD
            dslam_snapshots = DSLAMICMPSnapshot.objects.filter(
                dslam_id=dslam.id
            ).get(created_at__gte=date_start, created_at__lt=date_end)
            return Response({'result': serialize('json',[dslam_snapshots,])})


    @detail_route(methods=['GET'])
    def dslam_current_icmp_result(self, request, pk=None):
        user = request.user
        dslam = self.get_object()
        try:
            dslamicmp_obj = DSLAMICMP.objects.get(dslam=dslam)
        except:
            return Response({'result': 'Dont Still Add This DSLAM For Getting ICMP Protocol Result'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'result': serialize('json',[dslamicmp_obj])})


    @detail_route(methods=['GET'])
    def dslamslot(self, request, pk=None):
        user = request.user
        dslam = self.get_object()
        if dslam:
            query = '''select distinct(slot_number) from dslam_dslamport where dslam_id={0} order by slot_number'''.format(dslam.id)
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            results = {'slot_numbers':[row[0] for row in rows]}
            json_data = json.dumps(results)
            return HttpResponse(json_data, content_type="application/json")


    @detail_route(methods=['GET'])
    def board(self, request, pk=None):
        user = request.user
        dslam = self.get_object()
        if dslam:
            dslamboard_objs = DSLAMBoard.objects.filter(dslam=dslam)

        boards = [board.as_json() for board in dslamboard_objs]
        return HttpResponse(json.dumps(boards), content_type="application/json")


class DSLAMCartViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    queryset = DSLAMCart.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = DSLAMCartSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        queryset = self.queryset
        telecom_id = self.request.query_params.get('telecom_center_id',None)
        if telecom_id:
            queryset = queryset.filter(telecom_center__id=telecom_id)
        return queryset


    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class DSLAMLocationViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):

    permission_classes = (IsAuthenticated, HasAccessToDslam)
    serializer_class = DSLAMLocationSerializer
    paginate_by = None
    paginate_by_param = None
    paginator = None

    def get_queryset(self):
        queryset = DSLAMLocation.objects.all()

        telecom_id = self.request.query_params.get('telecom-center',None)
        city_id = self.request.query_params.get('city_id',None)
        dslam_id = self.request.query_params.get('dslam_id',None)

        if dslam_id:
            dslam_obj = DSLAM.objects.get(id=dslam_id)
            queryset = queryset.filter(dslam=dslam_obj)

        if city_id is not None and city_id !=u'' and not telecom_id:
            city = City.objects.get(id=city_id)
            telecom_objs = TelecomCenter.objects.filter(city=city)
            queryset = queryset.filter(dslam__telecom_center__in = telecom_objs)

        if queryset.count()>0:
            if telecom_id:
                telecom_obj = TelecomCenter.objects.get(id=telecom_id)
                queryset = queryset.filter(dslam__telecom_center__in=[telecom_obj,])

        return queryset

    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        dslam_name = DSLAM.objects.get(id=request.data['dslam']).name
        description = u'Add DSLAM Location , DSLAM: {0} - lat: {1} - long: {2}'.format(
                dslam_name,
                request.data['dslam_lat'],
                request.data['dslam_long'])
        add_audit_log(request, 'DSLAMLocation', serializer.data['id'], 'Add DSLAM Location', description)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        description = u'Update DSLAM Location, DSLAM: {0} - params: {1}'.format(instance.dslam.name, request.data)
        add_audit_log(request, 'DSLAM', instance.id, 'Update DSLAM Location', description)
        return Response(serializer.data)


    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        description = u'Delete DSLAM Location, DSLAM: {0}'.format(instance.dslam.name)
        add_audit_log(request, 'DSLAM', instance.id, 'Delete DSLAM', description)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DSLAMEventViewsSet(mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):

    permission_classes = (IsAuthenticated, HasAccessToDslam)
    serializer_class = DSLAMEventSerializer
    queryset = DSLAMEvent.objects.all()

    def get_queryset(self):
        queryset = DSLAMEvent.objects.all()
        status = self.request.query_params.get('search_status',None)
        event_type = self.request.query_params.get('search_event_type',None)
        dslam_name = self.request.query_params.get('search_dslam_name',None)
        sort_field = self.request.query_params.get('sort_field',None)

        if status:
            queryset = queryset.filter(status=status)

        if dslam_name:
            dslam = DSLAM.objects.get(name=dslam_name)
            queryset = queryset.filter(dslam=dslam)

        if event_type:
            queryset = queryset.filter(type=event_type)

        if sort_field:
            queryset = queryset.order_by(sort_field)
        return queryset

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = DSLAMEventSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_instance = serializer.save()
        description = u'Update DSLAM Event, DSLAM: {0} - params: {1}'.format(new_instance.dslam.name, request.data)
        add_audit_log(request, 'DSLAM', new_instance.id, 'Update DSLAM Event', description)
        return Response(serializer.data)


    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        description = u'Delete DSLAM Event, DSLAM: {0}'.format(instance.dslam.name)
        add_audit_log(request, 'DSLAM', instance.id, 'Delete DSLAM Event', description)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DSLAMPortEventViewsSet(mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, HasAccessToDslam)
    serializer_class = DSLAMPortEventSerializer
    queryset = DSLAMPortEvent.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = DSLAMEventSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_instance = serializer.save()
        description = u'Update DSLAM Port Event,  DSLAM: {0} - Card: {1} - Slot: {2}, params: {3}'.format(
                new_instance.dslam.name,
                new_instance.slot_number,
                new_instance.port_number,
                request.data)
        add_audit_log(request, 'DSLAM', new_instance.id, 'Update DSLAM Event', description)
        return Response(serializer.data)


    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        description = u'Delete DSLAM Port Event,  DSLAM: {0} - Card: {1} - Slot: {2}, params: {3}'.format(
                instance.dslam.name,
                instance.slot_number,
                instance.port_number)
        add_audit_log(request, 'DSLAM', instance.id, 'Delete DSLAM Port Event', description)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DSLAMRunICMPCommandView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(),)

    def post(self, request, format=None):
        self.user = request.user
        data = request.data
        icmp_type = data.get('icmp_type')
        params = data.get('params')
        dslam_id = data.get('dslam_id')
        result = utility.run_icmp_command(dslam_id, icmp_type, params)

        dslam_name = DSLAM.objects.get(id=dslam_id).name

        description = u'Run {0} Command on DSLAM {1} with params: {2}'.format(icmp_type, dslam_name, params)
        add_audit_log(request, 'DSLAMICMP', None, 'Run ICMP Command on DSLAM', description)

        return Response({'result':result}, status=status.HTTP_201_CREATED)



class DSLAMPortRunCommandView(views.APIView):



    def post(self, request, format=None):
        user = request.user
        data = request.data
        command = data.get('command', None)
        dslam_id = data.get('dslam_id', None)
        params = data.get('params', None)
        try:
            dslam_obj = DSLAM.objects.get(id=dslam_id)
       
        except Exception as ex:
            return JsonResponse({'result':str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        logging.info(command)
        if not command:
            return Response({'result': 'Command does not exits'}, status=status.HTTP_400_BAD_REQUEST)
        params["username"] = user.username
        logging.info(params)
        result = utility.dslam_port_run_command(dslam_obj.pk, command, params)
        print (result)
        logging.info(user.username)

        if result:
            logging.info(result)
            if 'Busy' in result:
                return Response({'result': result}, status=status.HTTP_400_BAD_REQUEST)
            else:
                description = u'Run Command {0} on DSLAM {1}'.format(
                    command,
                    dslam_obj.name)

                add_audit_log(request, 'DSLAMCommand', None, 'Run Command On DSLAM Port', description)
        logging.info(user.username)
        return Response({'result': result}, status=status.HTTP_202_ACCEPTED)



class GetPortInfoView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(),)

    def post(self, request, format=None):
        user = request.user
        data = request.data
        try:
            dslam_obj = DSLAM.objects.get(id=int(data['dslam_id']))
        except:
            return Response({'result': 'Invalid dslam_id'}, status=status.HTTP_400_BAD_REQUEST)

        port_id = data.get('port_id', None)
        if not port_id:
            return Response({'result': 'Invalid port_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            port_obj = DSLAMPort.objects.get(dslam=dslam_obj, id=port_id)
        except:
            return Response({'result': 'Port does not exists'}, status=status.HTTP_404_NOT_FOUND)

        if user.type == 'RESELLER':
            if not user.reseller.resellerport_set.filter(
                    port_name=port_obj.port_name,
                    dslam=dslam_obj,
            ).exists():
                return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        utility.get_port_info(dslam_obj.pk, port_obj.pk)
        return Response({'messege':'params posted'})


class ResetAdminStatusView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(),)

    def post(self, request, format=None):
        user = request.user
        data = request.data
        try:
            dslam_obj = DSLAM.objects.get(id=int(data['dslam_id']))
        except:
            return Response({'result': 'Invalid dslam_id'}, status=status.HTTP_400_BAD_REQUEST)

        port_id = data.get('port_id', None)
        if not port_id:
            return Response({'result': 'Invalid port_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            port_obj = DSLAMPort.objects.get(dslam=dslam_obj, id=port_id)
        except:
            return Response({'result': 'Port does not exists'}, status=status.HTTP_404_NOT_FOUND)

        if user.type == 'RESELLER':
            if not user.reseller.resellerport_set.filter(
                    port_name=port_obj.port_name,
                    dslam=dslam_obj,
            ).exists():
                return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        result = utility.reset_admin_status(dslam_obj.pk, port_obj.pk)
        description = u'Reset Admin Status on DSLAM {0} Card {1} port {2}'.format(
                    dslam_obj.name,
                    port_obj.slot_number,
                    port_obj.port_number)
        add_audit_log(request, 'DSLAMCommand', None, 'Reset Admin Status Port', description)
        return Response({'messege':result})


class ChangePortAdminStatusView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(),)

    def post(self, request, format=None):
        user = request.user
        data = request.data
        try:
            dslam_obj = DSLAM.objects.get(id=int(data['dslam_id']))
        except:
            return Response({'result': 'Invalid dslam_id'}, status=status.HTTP_400_BAD_REQUEST)

        port_id = data.get('port_id', None)
        if not port_id:
            return Response({'result': 'Invalid port_id'}, status=status.HTTP_400_BAD_REQUEST)

        new_status = data.get('new_status', None)
        if not new_status:
            return Response({'result': 'new_status does not exists'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            port_obj = DSLAMPort.objects.get(dslam=dslam_obj, id=port_id)
        except:
            return Response({'result': 'Port does not exists'}, status=status.HTTP_404_NOT_FOUND)

        if user.type == 'RESELLER':
            if not user.reseller.resellerport_set.filter(
                    port_name=port_obj.port_name,
                    dslam=dslam_obj,
            ).exists():
                return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        result = utility.change_port_admin_status(dslam_obj.pk, port_obj.pk, new_status)
        description = u'Change Admin Status on DSLAM {0} Card {1} port {2} to new status {3}'.format(
                    dslam_obj.name,
                    port_obj.slot_number,
                    port_obj.port_number,
                    new_status)
        add_audit_log(request, 'DSLAMCommand', None, 'Change Admin Status Port', description)
        return Response({'messege':result})


class ChangePortLineProfileView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(),)

    def post(self, request, format=None):
        user = request.user
        data = request.data
        try:
            dslam_obj = DSLAM.objects.get(id=int(data['dslam_id']))
        except:
            return Response({'result': 'Invalid dslam_id'}, status=status.HTTP_400_BAD_REQUEST)

        port_id = data.get('port_id', None)
        if not port_id:
            return Response({'result': 'Invalid port_id'}, status=status.HTTP_400_BAD_REQUEST)

        new_line_profile = data.get('new_line_profile', None)
        if not new_line_profile:
            return Response({'result': 'new_line_profile does not exists'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            port_obj = DSLAMPort.objects.get(dslam=dslam_obj, id=port_id)
        except:
            return Response({'result': 'Port does not exists'}, status=status.HTTP_404_NOT_FOUND)

        if user.type == 'RESELLER':
            if not user.reseller.resellerport_set.filter(
                    port_name=port_obj.port_name,
                    dslam=dslam_obj,
            ).exists():
                return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        new_line_profile_name = LineProfile.objects.get(id=new_line_profile).name
        result = utility.change_port_line_profile(dslam_obj.pk, port_obj.pk, new_line_profile_name)
        description = u'Change Line Profile on DSLAM {0} Card {1} port {2} to new line profile {3}'.format(
                    dslam_obj.name,
                    port_obj.slot_number,
                    port_obj.port_number,
                    new_line_profile)
        add_audit_log(request, 'DSLAMCommand', None, 'Change Line Profile Port', description)
        return Response({'messege':result})


class DSLAMTypeViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    serializer_class = DSLAMTypeSerializer
    permission_classes = (IsAuthenticated, )
    queryset = DSLAMType.objects.all()
    paginate_by = None
    paginate_by_param = None
    paginator = None


    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        description = u'Delete DSLAM type {0} '.format(instance.name)
        add_audit_log(request, 'DSLAMType', instance.id, 'Delete DSLAM Type', description)
        return Response(status=status.HTTP_204_NO_CONTENT)


    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        city_name = City.objects.get(id=serializer.data['city']).name
        description = u'Add DSLAM Type {0}'.format(serializer.data['name'])
        add_audit_log(request, 'DSLAMType', serializer.data['id'], 'Add DSLAM type', description)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        description = u'Update DSLAM type {0}, params: {1}'.format(instance.name, request.data)
        add_audit_log(request, 'DSLAMType', instance.id, 'Update DSLAM Type', description)
        return Response(serializer.data)



class CommandViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    serializer_class = CommandSerializer
    permission_classes = (IsAuthenticated, )
    queryset = Command.objects.all()
    paginate_by = None
    paginate_by_param = None
    paginator = None

    def get_queryset(self):
        queryset = self.queryset
        command_type = self.request.query_params.get('type', None)
        dslam_id = self.request.query_params.get('dslam_id', None)
        command_type = self.request.query_params.get('type', None)
        exclude_type = self.request.query_params.get('exclude_type', None)
        command_name = self.request.query_params.get('command_name', None)
        exclude_command_ids = self.request.query_params.get('exclude_command_id', None)

        if dslam_id:
            dslam_type = DSLAM.objects.get(id=dslam_id).dslam_type
            command_ids = DSLAMTypeCommand.objects.filter(dslam_type=dslam_type).values_list('command__id', flat=True)
            queryset = queryset.filter(id__in=command_ids)

        if exclude_command_ids:
            exclude_command_ids = eval(exclude_command_ids)
            if exclude_command_ids or len(exclude_command_ids) > 0:
                queryset = queryset.exclude(id__in=exclude_command_ids)
        show_command = self.request.query_params.get('show_command', None)
        if show_command:
            queryset = queryset.filter(show_command=show_command)
        if command_type:
            queryset = queryset.filter(type=command_type)
        if exclude_type:
            queryset = queryset.exclude(type=exclude_type)
        if command_name:
            queryset = queryset.filter(text__icontains=command_name)
        return queryset

    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        description = u'Delete Command {0} '.format(instance.name)
        add_audit_log(request, 'Command', instance.id, 'Delete Command', description)
        return Response(status=status.HTTP_204_NO_CONTENT)



    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        city_name = City.objects.get(id=serializer.data['city']).name
        description = u'Add Command {0}'.format(serializer.data['name'])
        add_audit_log(request, 'Command', serializer.data['id'], 'Add Command', description)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        description = u'Update Command {0}, params: {1}'.format(instance.name, request.data)
        add_audit_log(request, 'Command', instance.id, 'Update Command', description)
        return Response(serializer.data)


class CityViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    serializer_class = CitySerializer
    permission_classes = (IsAuthenticated, )

    @list_route(methods=['GET'])
    def tree_view(self,request):
        q = '''select id,name as text, abbr, english_name ,parent_id from dslam_city order by id desc'''
        cursor = connection.cursor()
        cursor.execute(q)
        rows = cursor.fetchall()
        result = []
        parent = '#'

        keys = ('id', 'text', 'abbr', 'english_name', 'parent')
        for row in rows:
            if row[4] == None:
                city_row=(row[0],row[1], row[2], row[3], '#')
            else:
                city_row = row
            result.append(dict(zip(keys,city_row)))
        json_data = json.dumps(sorted(result, key=lambda k: k['id']))
        return HttpResponse(json_data, content_type="application/json")

    @list_route(methods=['GET'])
    def table_view(self,request):
        q = '''select a.id,a.name,b.name from dslam_city a left join dslam_city b on a.parent_id = b.id order by a.id desc'''
        cursor = connection.cursor()
        cursor.execute(q)
        rows = cursor.fetchall()
        result = []
        parent = '#'

        keys = ('id','name','parent',)
        for row in rows:
            if row[2] == None:
                city_row=(row[0],row[1],'#')
            else:
                city_row = row
            result.append(dict(zip(keys,city_row)))
        json_data = json.dumps(sorted(result, key=lambda k: k['id']))
        return HttpResponse(json_data, content_type="application/json")

    def get_queryset(self):
        queryset = City.objects.all()
        parent = self.request.query_params.get('parent', None)
        city_name = self.request.query_params.get('city_name', None)
        if parent:
            if parent == 'all':
                queryset = queryset.filter(parent=None)
            elif parent == 'never':
                queryset = queryset.exclude(parent=None)
            else:
                try:
                    queryset = queryset.filter(parent=parent)
                except:
                    pass
        if city_name:
            queryset = queryset.filter(Q(name__icontains=city_name) | Q(english_name__icontains=city_name))
        return queryset


    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        description = u'Delete City {0} '.format(instance.name)
        add_audit_log(request, 'City', instance.id, 'Delete City', description)
        return Response(status=status.HTTP_204_NO_CONTENT)



    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        city_name = serializer.data['name']
        description = u'Add City {0}'.format(city_name)
        add_audit_log(request, 'City', serializer.data['id'], 'Add City', description)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        description = u'Update City {0}, params: {1}'.format(instance.name, request.data)
        add_audit_log(request, 'City', instance.id, 'Update City', description)
        return Response(serializer.data)


class CityLocationViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    serializer_class = CityLocationSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)
    paginate_by = None
    paginate_by_param = None
    paginator = None

    def get_queryset(self):
        user = self.request.user
        city_id = self.request.query_params.get('city_id', None)
        queryset = CityLocation.objects.all()
        if city_id:
            city = City.objects.get(id=city_id)
            queryset = queryset.filter(city=city)
        return queryset


    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        description = u'Delete City {0} Location'.format(instance.city.name)
        add_audit_log(request, 'CityLocation', instance.id, 'Delete City Location', description)
        return Response(status=status.HTTP_204_NO_CONTENT)



    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        city_name = City.objects.get(id=serializer.data['city']).name
        description = u'Add City Location , City: {0} - lat: {1} - long: {2}'.format(
                city_name,
                serializer.data['city_lat'],
                serializer.data['city_long'])
        add_audit_log(request, 'CityLocation', serializer.data['id'], 'Add City Location', description)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        description = u'Update City Location , City: {0} - lat: {1} - long: {2}'.format(
                instance.city.name,
                request.data['city_lat'],
                request.data['city_long'])
        add_audit_log(request, 'CityLocation', instance.id, 'Update City Location', description)
        return Response(serializer.data)


class TelecomCenterViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    serializer_class = TelecomCenterSerializer
    permission_classes = (IsAuthenticated, TelecomCenterView, TelecomCenterEdit)
    queryset = TelecomCenter.objects.all()

    def destroy(self,request, *args, **kwargs):
        telecom_center = self.get_object()
        dslam_count = DSLAM.objects.filter(telecom_center=telecom_center).count()
        if dslam_count > 0:
            return Response({'msg':'this telecom used in dslams'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            self.perform_destroy(telecom_center)
            description = u'Delete Telecom Center {0}'.format(telecom_center.name)
            add_audit_log(request, 'TelecomCenter', telecom_center.id, 'Delete Telecom Center', description)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('search_name', None)
        prefix_bukht_name = self.request.query_params.get('search_prefix_bukht_name', None)
        city_id = self.request.query_params.get('search_city_id', None)
        city_name = self.request.query_params.get('search_city_name', None)

        orderby = self.request.query_params.get('sort_field',None)

        if city_name:
            city_ids = City.objects.all().filter(name__icontains=city_name).values_list('id', flat=True)
            qCity = Q()
            for city_id in city_ids:
                qCity &= Q(city__id=city_id)
            queryset= queryset.filter(qCity)

        if city_id:
            city_obj = City.objects.get(id=city_id)
            if city_obj.parent == None:
                city_ids = City.objects.filter(parent=city_obj).values_list('id', flat=True)
                queryset = queryset.filter(city__id__in=city_ids)
            else:
                queryset = queryset.filter(city=city_obj)

        if name:
            queryset = queryset.filter(name__istartswith=name)

        if prefix_bukht_name:
            queryset = queryset.filter(prefix_bukht_name__icontains=prefix_bukht_name)

        if orderby:
            queryset = queryset.order_by(orderby)

        return queryset

    @list_route(methods=['GET'])
    def get_without_paging(self, request):
        telecom_objs = TelecomCenter.objects.all()
        data = request.query_params
        city_id = data.get('city_id')
        if city_id:
            try:
                city_obj = City.objects.get(id=city_id)
                if city_obj.parent == None:
                    city_ids = City.objects.filter(parent=city_obj).values_list('id', flat=True)
                    telecom_objs = telecom_objs.filter(city__id__in=city_ids)
                else:
                    telecom_objs = telecom_objs.filter(city=city_obj)

            except:
                return Response({'result': 'city_id does not exists'}, status=status.HTTP_400_BAD_REQUEST)
        data = [item.as_json() for item in telecom_objs]
        return HttpResponse(json.dumps(data), content_type='application/json; charset=UTF-8')

    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        description = u'Create Telecom Center {0}'.format(serializer.data['name'])
        add_audit_log(request, 'TelecomCenter', serializer.data['id'], 'Create Telecome Center', description)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        description = u'Update Telecom Center {0}: {1}'.format(instance.name, request.data)
        add_audit_log(request, 'TelecomCenter', instance.id, 'Update Telecom Center', description)
        return Response(serializer.data)


class TelecomCenterLocationViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    serializer_class = TelecomCenterLocationSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)
    paginate_by = None
    paginate_by_param = None
    paginator = None

    def get_queryset(self):
        user = self.request.user
        queryset = TelecomCenterLocation.objects.all()
        telecom_id = self.request.query_params.get('telecom_id', None)
        if telecom_id:
            queryset = queryset.filter(telecom_center__id = telecom_id)
        return queryset

    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class DSLAMPortViewSet(mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    serializer_class = DSLAMPortSerializer
    queryset = DSLAMPort.objects.all().order_by('port_index')
    permission_classes = (IsAuthenticated, DSLAMPortView, DSLAMPortEdit)
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset

        dslam_name = self.request.query_params.get('search_dslam_name', None)
        dslam_ip = self.request.query_params.get('search_dslam_ip', None)
        dslam_id = self.request.query_params.get('search_dslam_id', None)
        port_name = self.request.query_params.get('search_port_name', None)
        port_index = self.request.query_params.get('search_port_index', None)
        telecom_id = self.request.query_params.get('search_telecom', None)
        oper_status = self.request.query_params.get('search_oper_status', None)
        admin_status = self.request.query_params.get('search_admin_status', None)
        sort_field = self.request.query_params.get('sort_field', None)
        city_id = self.request.query_params.get('search_city',None)
        vlan_obj_id = self.request.query_params.get('search_vlan_id',None)
        line_profile = self.request.query_params.get('search_line_profile',None)
        down_attainable_rate_range = self.request.query_params.get('search_down_attainable_rate_range',None)
        up_attainable_rate_range = self.request.query_params.get('search_up_attainable_rate_range',None)
        down_attenuation_range = self.request.query_params.get('search_down_attenuation_range',None)
        up_attenuation_range = self.request.query_params.get('search_up_attenuation_range',None)
        down_snr_range = self.request.query_params.get('search_down_snr_range',None)
        up_snr_range = self.request.query_params.get('search_up_snr_range',None)
        down_tx_rate_range = self.request.query_params.get('search_down_tx_rate_range',None)
        up_tx_rate_range = self.request.query_params.get('search_up_tx_rate_range',None)
        down_snr_flag = self.request.query_params.get('search_down_snr_flag',None)
        up_snr_flag = self.request.query_params.get('search_up_snr_flag',None)
        down_atten_flag = self.request.query_params.get('search_down_atten_flag',None)
        up_atten_flag = self.request.query_params.get('search_up_atten_flag',None)
        slot_number = self.request.query_params.get('search_slot_number', None)
        port_number = self.request.query_params.get('search_port_number', None)
        slot_number_from = self.request.query_params.get('search_slot_from', None)
        slot_number_to = self.request.query_params.get('search_slot_to', None)
        port_number_from = self.request.query_params.get('search_port_from', None)
        port_number_to = self.request.query_params.get('search_port_to', None)
        mac_address = self.request.query_params.get('search_mac_address', None)
        username = self.request.query_params.get('search_username', None)
        identifier_keys = [self.request.query_params.get('search_identifier_key', None)]

        if slot_number:
            queryset = queryset.filter(slot_number=slot_number)

        if port_number:
            queryset = queryset.filter(port_number=port_number)

        if slot_number_from:
            if slot_number_to:
                queryset = queryset.filter(
                        slot_number__gte=slot_number_from,
                        slot_number__lt=slot_number_to)
            else:
                queryset = queryset.filter(slot_number__gte=slot_number_from)

        if port_number_from:
            if port_number_to:
                queryset = queryset.filter(
                        port_number__gte=port_number_from,
                        port_number__lt=port_number_to)
            else:
                queryset = queryset.filter(port_number__gte=port_number_from)

        if down_snr_flag:
            queryset = queryset.filter(downstream_snr_flag=down_snr_flag)

        if up_snr_flag:
            queryset = queryset.filter(upstream_snr_flag=up_snr_flag)

        if down_atten_flag:
            queryset = queryset.filter(downstream_attenuation_flag=down_atten_flag)

        if up_atten_flag:
            queryset = queryset.filter(upstream_attenuation_flag=up_atten_flag)

        if down_attainable_rate_range:
            down_attainable_rate_range = eval(down_attainable_rate_range)
            queryset = queryset.filter(downstream_attainable_rate__gte=down_attainable_rate_range['from'],\
                    downstream_attainable_rate__lt=down_attainable_rate_range['to'])

        if up_attainable_rate_range:
            up_attainable_rate_range = eval(up_attainable_rate_range)
            queryset = queryset.filter(upstream_attainable_rate__gte=up_attainable_rate_range['from'],\
                    upstream_attainable_rate__lt=up_attainable_rate_range['to'])

        if down_attenuation_range:
            down_attenuation_range = eval(down_attenuation_range)
            queryset= queryset.filter(downstream_attenuation__gte=down_attenuation_range['from'],\
                    downstream_attenuation__lt=down_attenuation_range['to'])

        if up_attenuation_range:
            up_attenuation_range = eval(up_attenuation_range)
            queryset= queryset.filter(upstream_attenuation__gte=up_attenuation_range['from'],\
                    upstream_attenuation__lt=up_attenuation_range['to'])

        if down_snr_range:
            down_snr_range = eval(down_snr_range)
            queryset= queryset.filter(downstream_snr__gte=down_snr_range['from'],\
                   downstream_snr__lt=down_snr_range['to'])

        if up_snr_range:
            up_snr_range = eval(up_snr_range)
            queryset= queryset.filter(upstream_snr__gte=up_snr_range['from'],\
                    upstream_snr__lt=up_snr_range['to'])

        if down_tx_rate_range:
            down_tx_rate_range = eval(down_tx_rate_range)
            queryset= queryset.filter(downstream_tx_rate__gte=down_tx_rate_range['from'],\
                   downstream_tx_rate__lt=down_tx_rate_range['to'])

        if up_tx_rate_range:
            up_tx_rate_range = eval(up_tx_rate_range)
            queryset= queryset.filter(upstream_tx_rate__gte=up_tx_rate_range['from'],\
                    upstream_tx_rate__lt=up_tx_rate_range['to'])

        if city_id:
            telecom_ids = TelecomCenter.objects.filter(city__id=city_id).values_list('id', flat=True)
            dslam_ids = DSLAM.objects.filter(telecom_center__id__in=telecom_ids).values_list('id', flat=True)
            queryset= queryset.filter(dslam__id__in=dslam_ids)

        if telecom_id:
            dslam_ids = DSLAM.objects.filter(telecom_center__id=telecom_id).values_list('id', flat=True)
            queryset= queryset.filter(dslam__id__in=dslam_ids)

        if dslam_id:
            queryset= queryset.filter(dslam__id=dslam_id)

        if dslam_name:
            queryset = queryset.filter(dslam__name__istartswith=dslam_name)

        if dslam_ip:
            if len(dslam_ip.split('.')) != 4:
                queryset= queryset.filter(dslam__ip__istartswith=dslam_ip)
            else:
                queryset= queryset.filter(dslam__ip=dslam_ip)

        if port_name:
            queryset = queryset.filter(port_name=port_name)

        if port_index:
            queryset = queryset.filter(port_index=port_index)

        if line_profile:
            queryset= queryset.filter(line_profile=line_profile)

        if admin_status:
            queryset = queryset.filter(admin_status=admin_status)

        if oper_status:
            queryset = queryset.filter(oper_status=oper_status)

        if vlan_obj_id:
            ports_id = DSLAMPortVlan.objects.filter(vlan__id=vlan_obj_id).values_list('port', flat=True)
            queryset = queryset.filter(id__in=ports_id)

        if sort_field :
            queryset = queryset.order_by(sort_field)

        if mac_address:
            port_ids = DSLAMPortMac.objects.filter(mac_address=mac_address).values_list('port__id', flat=True)
            queryset = queryset.filter(id__in=port_ids)

        if username:
            identifier_keys = CustomerPort.objects.filter(username=username).values_list('identifier_key', flat=True)

        if identifier_keys[0]:
            mdf_dslam_objs = MDFDSLAM.objects.filter(identifier_key__in=identifier_keys).values('dslam_id', 'slot_number', 'port_number')
            port_ids = []
            for mdf_dslam_obj in mdf_dslam_objs:
                port_ids.append(DSLAMPort.objects.get(
                        dslam_id=mdf_dslam_obj['dslam_id'],
                        slot_number=mdf_dslam_obj['slot_number'],
                        port_number=mdf_dslam_obj['port_number']).pk)
            queryset = queryset.filter(id__in=port_ids)

        return queryset

    @detail_route(methods=['GET'])
    def mac_address(self, request, pk=None):
        user = request.user
        port_obj = self.get_object()
        port_macs = DSLAMPortMac.objects.filter(port=port_obj).values_list('mac_address', flat=True)
        return Response({'mac': port_macs})

    @detail_route(methods=['GET'])
    def report(self, request, pk=None):
        user = request.user
        port_obj = self.get_object()
        dslam_id = port_obj.dslam.id
        start_date = self.request.query_params.get('start_date',None)
        end_date = self.request.query_params.get('end_date',None)
        if start_date:
            #for example start_date = 20120505 and end_date = 20120606
            start_date = datetime.strptime(start_date[0:4]+'-'+start_date[4:6]+'-'+start_date[6:8], '%Y-%m-%d').date()
            if end_date:
                end_date = datetime.strptime(end_date[0:4]+'-'+end_date[4:6]+'-'+end_date[6:8], '%Y-%m-%d').date()
            else:
                end_date = date.today()

            port_snapshots = DSLAMPortSnapshot.objects.filter(
                dslam_id=dslam_id, port_index=port_obj.port_index
            ).filter(snp_date__gte=start_date,snp_date__lt=end_date).order_by('snp_date')

        else:
            now = datetime.now()
            DD = timedelta(weeks=1)
            date_from = now - DD
            port_snapshots = DSLAMPortSnapshot.objects.filter(
                dslam_id=dslam_id, port_index=port_obj.port_index
            ).filter(snp_date__gte=date_from).order_by('snp_date')

        up_snr_data, down_snr_data = [], []
        up_tx_rate, down_tx_rate = [], []
        up_attenuation, down_attenuation = [], []
        up_attainable_rate, down_attainable_rate = [], []

        oper_status = {'SYNC':0, 'NO-SYNC':0, 'OTHER':0}#up_count, down_count
        dates = []
        for snp in port_snapshots:
            dates.append(snp.snp_date.strftime('%Y-%m-%d %H:%M'))
            if snp.oper_status in ['SYNC', 'NO-SYNC']:
                oper_status[snp.oper_status]+=1
            else:
                oper_status['OTHER'] += 1

            up_snr_data.append(snp.upstream_snr)
            down_snr_data.append(snp.downstream_snr)
            up_tx_rate.append(snp.upstream_tx_rate)
            down_tx_rate.append(snp.downstream_tx_rate)
            up_attenuation.append(snp.upstream_attenuation)
            down_attenuation.append(snp.downstream_attenuation)
            up_attainable_rate.append(snp.upstream_attainable_rate)
            down_attainable_rate.append(snp.downstream_attainable_rate)

        snr_data = [{'name':'UP Stream SNR', 'data':up_snr_data}, {'name':'DOWN Stream SNR', 'data':down_snr_data}]
        attenuation_data = [{'name':'UP Stream Attenuation', 'data':up_attenuation},
                            {'name':'DOWN Stream Attenuation', 'data':down_attenuation}]
        tx_data = [{'name':'Down Stream TX Rate', 'data':down_tx_rate}, {'name':'UP Stream TX Rate', 'data':up_tx_rate}]
        attainable_rate_data = [{'name':'UP Stream Attainable Rate', 'data':up_attainable_rate},
                                {'name':'DOWN Stream Attainable Rate', 'data':down_attainable_rate}]
        oper_status_data = {'data': [{'name':name, 'y':value} for name,value in oper_status.iteritems()]}

        return JsonResponse(
                {'dates':json.dumps(dates),
                 'oper_status':json.dumps(oper_status_data),
                 'snr_data':json.dumps(snr_data),
                 'attenuation_data':json.dumps(attenuation_data),
                 'tx_data':json.dumps(tx_data),
                 'attainable_rate_data':json.dumps(attainable_rate_data),
                })


class PortStatusReportView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(), )

    def get(self, request, format=None):
        user = request.user

        slot_number = request.GET.get('slot_number', None)
        port_number = request.GET.get('port_number', None)
        start_date = self.request.query_params.get('start_date',None)
        end_date = self.request.query_params.get('end_date',None)

        try:
            dslam_obj = DSLAM.objects.get(id=int(request.GET['dslam_id']))
        except:
            return Response({'result': 'Invalid dslam_id'}, status=status.HTTP_400_BAD_REQUEST)

        if not port_number:
            return Response({'result': 'Invalid port number'}, status=status.HTTP_400_BAD_REQUEST)

        if not slot_number:
            return Response({'result': 'Invalid slot number'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            port_obj = DSLAMPort.objects.get(dslam=dslam_obj, port_number=port_number, slot_number=slot_number)
        except:
            return Response({'result': 'Port does not exists'}, status=status.HTTP_404_NOT_FOUND)


        #try:
        if start_date:
            #for example start_date = 20120505 and end_date = 20120606
            start_date = datetime.strptime(start_date[0:4]+'-'+start_date[4:6]+'-'+start_date[6:8], '%Y-%m-%d').date()
            if end_date:
                end_date = datetime.strptime(end_date[0:4]+'-'+end_date[4:6]+'-'+end_date[6:8], '%Y-%m-%d').date()
            else:
                end_date = date.today()

            port_snapshots = DSLAMPortSnapshot.objects.filter(
                dslam_id=dslam_obj.pk
            ).filter(
                port_index=port_obj.port_index
            ).filter(snp_date__gte=start_date,snp_date__lt=end_date).order_by('snp_date')

        else:
            now = datetime.now()
            DD = timedelta(weeks=1)
            date_from = now - DD
            port_snapshots = DSLAMPortSnapshot.objects.filter(
                dslam_id=dslam_obj.pk
            ).filter(
                port_index=port_obj.port_index
            ).filter(snp_date__gte=date_from).order_by('snp_date')

        up_snr_data, down_snr_data = [], []
        up_tx_rate, down_tx_rate = [], []
        up_attenuation, down_attenuation = [], []
        up_attainable_rate, down_attainable_rate = [], []

        oper_status = {'SYNC':0, 'NO-SYNC':0, 'OTHER':0}#up_count, down_count
        dates = []
        for snp in port_snapshots:
            dates.append(snp.snp_date.strftime('%Y-%m-%d %H:%M'))
            if snp.oper_status in ['SYNC', 'NO-SYNC']:
                oper_status[snp.oper_status]+=1
            else:
                oper_status['OTHER'] += 1

            up_snr_data.append(snp.upstream_snr)
            down_snr_data.append(snp.downstream_snr)
            up_tx_rate.append(snp.upstream_tx_rate)
            down_tx_rate.append(snp.downstream_tx_rate)
            up_attenuation.append(snp.upstream_attenuation)
            down_attenuation.append(snp.downstream_attenuation)
            up_attainable_rate.append(snp.upstream_attainable_rate)
            down_attainable_rate.append(snp.downstream_attainable_rate)

        snr_data = [{'name':'UP Stream SNR', 'data':up_snr_data}, {'name':'DOWN Stream SNR', 'data':down_snr_data}]
        attenuation_data = [{'name':'UP Stream Attenuation', 'data':up_attenuation},
                            {'name':'DOWN Stream Attenuation', 'data':down_attenuation}]
        tx_data = [{'name':'Down Stream TX Rate', 'data':down_tx_rate}, {'name':'UP Stream TX Rate', 'data':up_tx_rate}]
        attainable_rate_data = [{'name':'UP Stream Attainable Rate', 'data':up_attainable_rate},
                                {'name':'DOWN Stream Attainable Rate', 'data':down_attainable_rate}]
        oper_status_data = [{'name':name, 'y':value} for name,value in oper_status.iteritems()]
        reseller_obj = None
        customer_obj = None
        identifier_key = None
        try:
            identifier_key = MDFDSLAM.objects.get(dslam_id=port_obj.dslam.id, slot_number=port_obj.slot_number, port_number=port_obj.port_number).identifier_key

        except Exception as ex:
            print ex


        if identifier_key:
            try:
                customer = CustomerPort.objects.get(identifier_key=identifier_key)
                customer_obj = serialize('json',[customer])
            except Exception as ex:
                print ex

            try:
                reseller = ResellerPort.objects.get(identifier_key=identifier_key).reseller
                reseller_obj = serialize('json',[reseller])
            except Exception as ex:
                print ex

        dslamport_vlan_obj = DSLAMPortVlan.objects.filter(port=port_obj)
        vlan_obj_serializer = None
        if dslamport_vlan_obj.count() > 0:
            vlan_obj_serializer = serialize('json',[dslamport_vlan_obj.order_by('-created_at')[0].vlan])

        dslam_seializer_obj = serialize('json',[dslam_obj])
        dslam_json_obj = json.loads(dslam_seializer_obj)
        dslam_json_obj[0]['fields']['updated_at'] = JalaliDatetime(datetime.strptime(\
                ' '.join(dslam_json_obj[0]['fields']['updated_at'].split('T')).split('.')[0]\
                , "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S")
        dslam_json_obj[0]['fields']['created_at'] = JalaliDatetime(datetime.strptime(\
                ' '.join(dslam_json_obj[0]['fields']['created_at'].split('T')).split('.')[0]\
                , "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S")
        dslam_json_obj[0]['fields']['last_sync'] = JalaliDatetime(datetime.strptime(\
                ' '.join(dslam_json_obj[0]['fields']['last_sync'].split('T')).split('.')[0]\
                , "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S")


        dslamport_seializer_obj = serialize('json',[port_obj])

        dslamport_json_obj = json.loads(dslamport_seializer_obj)
        dslamport_json_obj[0]['fields']['updated_at'] = JalaliDatetime(datetime.strptime(\
                ' '.join(dslamport_json_obj[0]['fields']['updated_at'].split('T')).split('.')[0]\
                , "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S")
        dslamport_json_obj[0]['fields']['created_at'] = JalaliDatetime(datetime.strptime(\
                ' '.join(dslamport_json_obj[0]['fields']['created_at'].split('T')).split('.')[0]\
                , "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S")



        return JsonResponse(
                {'dslam':dslam_json_obj,
                 'port':dslamport_json_obj,
                 'dates':json.dumps(dates),
                 'oper_status':json.dumps(oper_status_data),
                 'snr_data':json.dumps(snr_data),
                 'attenuation_data':json.dumps(attenuation_data),
                 'tx_data':json.dumps(tx_data),
                 'customer':customer_obj,
                 'reseller':reseller_obj,
                 'attainable_rate_data':json.dumps(attainable_rate_data),
                 'port_vlan': vlan_obj_serializer
                })
        #except:
        #    return JsonResponse({'result':'error'})


class ResellerViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    serializer_class = ResellerSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get_queryset(self):
        reseller_queryset = Reseller.objects.all()
        name = self.request.query_params.get('name', None)
        tel = self.request.query_params.get('tel', None)
        fax = self.request.query_params.get('fax', None)
        address = self.request.query_params.get('address', None)
        city_id = self.request.query_params.get('city_id', None)
        vpi = self.request.query_params.get('vpi', None)
        vci = self.request.query_params.get('vci', None)
        orderby = self.request.query_params.get('sort_field',None)

        if name:
            try:
                reseller_queryset = reseller_queryset.filter(name__icontains=name)
            except:
                pass
        if name:
            try:
                reseller_queryset = reseller_queryset.filter(name__icontains=name)
            except:
                pass
        if address:
            try:
                reseller_queryset = reseller_queryset.filter(address__icontains=address)
            except:
                pass
        if tel:
            try:
                reseller_queryset = reseller_queryset.filter(tel__contains=tel)
            except:
                pass
        if fax:
            try:
                reseller_queryset = reseller_queryset.filter(fax__contains=fax)
            except:
                pass
        if city_id:
            try :
                city = City.objects.get(id=city_id)
                reseller_queryset = reseller_queryset.filter(city=city)
            except:
                pass

        if orderby:
            reseller_queryset = reseller_queryset.order_by(orderby)

            if vpi:
                try:
                    reseller_queryset = reseller_queryset.filter(vpi=vpi)
                except:
                    pass

        return reseller_queryset


    @detail_route(methods=['GET'])
    def report(self, request, pk=None):
        user = request.user
        reseller_obj = self.get_object()
        telecom_center_ports = defaultdict(list)
        for reseller_port in ResellerPort.objects.filter(reseller=reseller_obj):
            telecom_center_ports[reseller_port.telecom_center_id].append(reseller_port.identifier_key)

        data = []

        total_ports_count = 0
        up_ports_count = 0
        down_ports_count = 0
        for telecom_center_id, identifier_keys in telecom_center_ports.iteritems():
            tc_object = TelecomCenter.objects.get(id=telecom_center_id)
            customer_port = set(CustomerPort.objects.filter(telecom_center_id=telecom_center_id).values_list('identifier_key', flat=True))

            intersection_port = set(identifier_keys).intersection(customer_port)

            total_ports_count += len(identifier_keys)
            up_ports_count += len(intersection_port)
            down_ports_count +=  len(identifier_keys) - len(intersection_port)

            data.append({
                'telecom_center': {'id': tc_object.id, 'name': tc_object.name} ,
                'total_ports_count': len(identifier_keys) ,
                'up_ports_count': len(intersection_port) ,
                'down_ports_count':  len(identifier_keys) - len(intersection_port) ,
                })

        return JsonResponse({
            'total_ports_count': total_ports_count,
            'up_ports_count': up_ports_count,
            'down_ports_count': down_ports_count,
            'data': data,
            })


class ResellerPortViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    serializer_class = ResellerPortSerializer
    permission_classes = (IsAuthenticated, HasAccessToDslamPort)

    def get_queryset(self):
        queryset = ResellerPort.objects.all()
        identifier_key = self.request.query_params.get('identifire_key', None)
        dslam_name = self.request.query_params.get('search_dslam_name', None)
        reseller_name = self.request.query_params.get('search_reseller_name', None)
        dslam_port_id = self.request.query_params.get('dslamport_id', None)
        orderby = self.request.query_params.get('sort_field',None)


        if dslam_port_id:
            port_obj = DSLAMPort.objects.get(id=dslam_port_id)
            try:
                identifier_key = MDFDSLAM.objects.get(dslam_id=port_obj.dslam_id, slot_number=port_obj.slot_number, port_number=port_obj.port_number).identifier_key
            except Exception as ex:
                print ex
                return []

        if identifier_key:
            print identifier_key
            queryset = queryset.filter(identifier_key=identifier_key)

        if dslam_name:
            dslam_ids = DSLAM.objects.filter(name__istartswith=dslam_name).values_list('id', flat=True)
            identifier_keys = MDFDSLAM.objects.filter(dslam_id__in=dslam_ids).values_list('identifier_key', flat=True)
            queryset = queryset.filter(identifier_key__in=identifier_keys)
        if reseller_name:
            reseller_ids = Reseller.objects.filter(name__istartswith=reseller_name).values_list('id', flat=True)
            queryset = queryset.filter(reseller__id__in=reseller_ids)

        if orderby:
            queryset = queryset.order_by(orderby)
        return queryset

    def create(self, request, *args, **kwargs):
        print request.data
        self.user = request.user
        dslam_id = request.data.get('dslam')
        slot_number = request.data.get('slot_number')
        slot_from = request.data.get('slot_number_from')
        slot_to = request.data.get('slot_number_to')

        port_number = request.data.get('port_number')
        port_to = request.data.get('port_number_to')
        port_from = request.data.get('port_number_from')

        reseller_id = request.data.get('reseller')
        identifier_key = request.data.get('identifier_key')
        vlan_id = request.data.get('vlan_id')

        dslam_obj = DSLAM.objects.get(id=dslam_id)
        print dslam_obj
        reseller_obj = Reseller.objects.get(id=reseller_id)


        if not reseller_id:
            return Response({'result': 'reseller_id does not exists'}, status=status.HTTP_400_BAD_REQUEST)
        reseller = Reseller.objects.get(id=reseller_id)


        if identifier_key:
            mdf_dslam_obj = MDFDSLAM.objects.get(identifier_key=identifier_key)
            mdf_dslams = ((mdf_dslam_obj.telecom_center_id, mdf_dslam_obj.slot_number, mdf_dslam_obj.port_number, mdf_dslam_obj.identifier_key),)

        elif port_number and slot_number and dslam_id and reseller_id:
            print 'here'
            t = MDFDSLAM.objects.filter(dslam_id=dslam_id)
            print t
            print '====='
            mdf_dslams = MDFDSLAM.objects.filter(
                    dslam_id=dslam_id,
                    slot_number=slot_number,
                    port_number=port_number).values_list(
                            'telecom_center_id',
                            'slot_number',
                            'port_number',
                            'identifier_key')

        elif slot_from and slot_to and port_from and port_to and port_from:
            mdf_dslams = MDFDSLAM.objects.filter(
                    dslam_id=dslam_id,
                    slot_number__gte=slot_from,
                    port_number__gte=port_from).filter(
                    slot_number__lte=slot_to,
                    port_number__lte=port_to).values_list('telecom_center_id', 'slot_number', 'port_number', 'identifier_key')
        else:
            return Response({'result': 'bad parameter send'}, status=status.HTTP_400_BAD_REQUEST)


        print mdf_dslams
        added_item = []
        exist_item = []
        port_indexes = []
        for telecom_center_id, slot_number, port_number,  identifier_key in mdf_dslams:
            try:
                rp = ResellerPort()
                rp.reseller = reseller
                rp.telecom_center_id = telecom_center_id
                rp.identifier_key = identifier_key
                rp.save()
                port_indexes.append({
                    'slot_number': slot_number,
                    'port_number': port_number,
                    'port_index': DSLAMPort.objects.get(dslam__id=dslam_id, port_number=port_number, slot_number=slot_number).port_index
                    })
                added_item.append({'reseller': reseller.name, 'identifier_key': identifier_key, 'slot_number': slot_number, 'port_number': port_number})
            except Exception as ex:
                exist_item.append({'reseller': reseller.name, 'identifier_key': identifier_key, 'slot_number': slot_number, 'port_number': port_number})

        if len(added_item) > 0:
            params = dict(vlan_id=vlan_id, port_indexes = port_indexes, username = self.user.username)

            result = utility.dslam_port_run_command(dslam_id, 'add to vlan', params)


        return Response({'exist_item':exist_item, 'added_item':added_item}, status=status.HTTP_201_CREATED)


class CustomerPortViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    serializer_class = CustomerPortSerializer
    permission_classes = (IsAuthenticated, HasAccessToDslamPort)
    queryset = CustomerPort.objects.all()

    def get_queryset(self):
        user = self.request.user
        customerports = self.queryset

        identifire_key = self.request.query_params.get('identifier_key', None)
        dslam_port_id = self.request.query_params.get('dslamport_id', None)
        firstname = self.request.query_params.get('firstname', None)
        lastname = self.request.query_params.get('lastname', None)
        username = self.request.query_params.get('username', None)
        tel = self.request.query_params.get('tel', None)
        mobile = self.request.query_params.get('mobile', None)
        email = self.request.query_params.get('email', None)
        national_code = self.request.query_params.get('national_code', None)
        sort_field = self.request.query_params.get('sort_field',None)

        if dslam_port_id:
            port_obj = DSLAMPort.objects.get(id=dslam_port_id)
            try:
                mdfdslam_obj = MDFDSLAM.objects.get(dslam_id=port_obj.dslam_id, slot_number=port_obj.slot_number, port_number=port_obj.port_number)
                customerports = customerports.filter(identifier_key=mdfdslam_obj.identifier_key)
            except Exception as ex:
                return []

        if identifire_key:
            try:
                customerports = customerports.filter(identifier_key__istartswith=identifire_key)
            except Exception as ex:
                print '=>', ex
                pass

        if firstname:
            try:
                customerports = customerports.filter(firstname__istartswith=firstname)
            except:
                pass
        if lastname:
            try:
                customerports = customerports.filter(lastname__istartswith=lastname)
            except:
                pass
        if username:
            try:
                customerports = customerports.filter(username__istartswith=username)
            except:
                pass
        if tel:
            try:
                customerports = customerports.filter(tel__istartswith=tel)
            except:
                pass
        if mobile:
            try:
                customerports = customerports.filter(mobile__istartswith=mobile)
            except:
                pass
        if email:
            try:
                customerports = customerports.filter(email=email)
            except Exception as ex:
                pass

        if national_code:
            try:
                customerports = customerports.filter(national_code__contains=national_code)
            except:
                pass
        if sort_field:
            customerports = customerports.order_by(sort_field)
        return customerports

    def create(self, request, *args, **kwargs):
        data = request.data

        identifier_key = data.get('identifier_key')
        username = data.get('username')
        params = data.get('params')
        vlan_obj_id = data.get('v_id')

        if identifier_key:
            try:
                mdf_dslam_obj = MDFDSLAM.objects.filter(identifier_key=identifier_key)[0]
            except Exception as ex:
                return Response({'result': \
                        'identifier_key does not exist'}, \
                        status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'result': \
                    'username or identifier_key does not exists'}, \
                    status=status.HTTP_400_BAD_REQUEST)

        if params.get('vlan_id') and int(params.get('vlan_id')) == 1:
            vlan_obj = Vlan.objects.get(vlan_id='1', reseller=None)
            params['vlan_id'] = vlan_obj.vlan_id
        elif vlan_obj_id:
            vlan_obj = Vlan.objects.get(id=vlan_obj_id)
            params['vlan_id'] = vlan_obj.vlan_id

        if 'port_conditions' not in params.keys():
            params['port_conditions'] = {'slot_number': mdf_dslam_obj.slot_number, 'port_number': mdf_dslam_obj.port_number}
            params['dslam_id'] = mdf_dslam_obj.dslam_id

        if params.get('vlan_id'):
            params["username"] = request.user.username
            result = utility.dslam_port_run_command(mdf_dslam_obj.dslam_id, 'port pvc set', params)
            if 'error' in result:
                return Response({'result': 'service is not available'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        port_obj = DSLAMPort.objects.get(
            dslam__id=mdf_dslam_obj.dslam_id,
            slot_number=mdf_dslam_obj.slot_number,
            port_number=mdf_dslam_obj.port_number)
        if params.get('vlan_id'):
            dslamport_vlan_obj, created_port_vlan_obj = DSLAMPortVlan.objects.get_or_create(
                        port=port_obj,
                        vlan=vlan_obj
                        )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        #End Port PVC Set

        headers = self.get_success_headers(serializer.data)
        description = u'Create Customer {0}'.format(serializer.data['username'])
        add_audit_log(request, 'Customer', serializer.data['id'], 'Create Customer', description)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['POST'])
    def activeport(self, request):
        user = request.user
        data = request.data
        identifier_key = data.get('identifier_key')
        username = data.get('username')
        params = data.get('params')
        vlan_obj_id = data.get('vlan_id')

        if username:
            identifier_key = CustomerPort.objects.get(username=username).identifier_key
        if identifier_key:
            try:
                mdf_dslam_obj = MDFDSLAM.objects.filter(identifier_key=identifier_key)[0]
            except Exception as ex:
                return Response({'result': \
                        'identifier_key does not exist'}, \
                        status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'result': \
                    'username or identifier_key does not exists'}, \
                    status=status.HTTP_400_BAD_REQUEST)

        if int(params.get('vlan_id')) == 1:
            vlan_obj = Vlan.objects.get(vlan_id='1' , reseller=None)
            params['vlan_id'] = vlan_obj.vlan_id
        elif vlan_obj_id:
            vlan_obj = Vlan.objects.get(id=vlan_obj_id)
            params['vlan_id'] = vlan_obj.vlan_id
        else:
            return Response({'result': \
                    'vlan_obj_id does not exist'}, \
                    status=status.HTTP_400_BAD_REQUEST)

        if 'card_ports' not in params.keys():
            params['port_indexes'] =[{'slot_number': mdf_dslam_obj.slot_number, 'port_number': mdf_dslam_obj.port_number}]
        if params.get('vlan_id'):
            params["username"] = user.username
            result = utility.dslam_port_run_command(mdf_dslam_obj.dslam_id, params.get('command'), params)
            if 'error' in result:
                return Response({'result': 'service is not available'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        port_obj = DSLAMPort.objects.get(
            dslam__id=mdf_dslam_obj.dslam_id,
            slot_number=mdf_dslam_obj.slot_number,
            port_number=mdf_dslam_obj.port_number)

        if params.get('vlan_id'):
            dslamport_vlan_obj, created_port_vlan_obj = DSLAMPortVlan.objects.get_or_create(
                        port=port_obj,
                        vlan=vlan_obj
                        )

        return Response({'result': 'Port Acitived'}, status=status.HTTP_201_CREATED)


    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        description = u'Update Customer Port {0}: {1}'.format(instance.name, request.data)
        add_audit_log(request, 'CustomerPort', instance.id, 'Update Customer Port', description)
        return Response(serializer.data)

class PortCommandViewSet(mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    serializer_class = PortCommandSerializer
    permission_classes = (IsAuthenticated, )
    paginate_by = None
    paginate_by_param = None
    paginator = None


    def get_queryset(self):
        user = self.request.user
        print '--------------------------'
        print self.request.query_params
        print '--------------------------'
        portcommands = PortCommand.objects.all().order_by('-created_at')

        dslam_id = self.request.query_params.get('dslam', None)
        dslamport_id = self.request.query_params.get('dslamport_id', None)
        slot_number = self.request.query_params.get('slot_number', None)
        port_number = self.request.query_params.get('port_number', None)
        port_index = self.request.query_params.get('port_index', None)
        limit_row = self.request.query_params.get('limit_row', None)
        command_type_id = self.request.query_params.get('command_type_id', None)
        command_type_name = self.request.query_params.get('command_type_name', None)

        port_obj = None
        if dslamport_id:
            try:
                port_obj = DSLAMPort.objects.get(id=dslamport_id)
            except Exception as ex:
                print ex
                return []

        elif slot_number and port_number and dslam_id:
            port_obj = DSLAMPort.objects.get(dslam__id=dslam_id, port_number=port_number, slot_number=slot_number)
        else:
            print '=>>>>>>>>> please send dslamport_id'
            return []

        if command_type_name:
            portcommands = portcommands.filter(command__text=command_type_name)
        elif command_type_id:
            portcommands = portcommands.filter(command__id=command_type_id)
        else:
            query = """SELECT id FROM
            (SELECT *,row_number() OVER(PARTITION BY card_ports->'card', card_ports->'port',command_id ORDER BY created_at DESC) as rnk FROM dslam_portcommand )
            as d WHERE rnk = 1"""
            portcommands = portcommands.extra(where=["id in (%s)"%query])

        if limit_row:
            portcommands = portcommands.filter(dslam__id=dslam_id, card_ports__contains=[{"slot_number": port_obj.slot_number, "port_number": port_obj.port_number}])[:int(limit_row)]
        else:
            portcommands = portcommands.filter(dslam__id=dslam_id, card_ports__contains=[{"slot_number": port_obj.slot_number, "port_number": port_obj.port_number}])
        return portcommands



class DSLAMCommandViewSet(mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    serializer_class = DSLAMCommandSerializer
    permission_classes = (IsAuthenticated, )
    queryset = DSLAMCommand.objects.all().order_by('-created_at')
    paginate_by = None
    paginate_by_param = None
    paginator = None

    def get_queryset(self):
        user = self.request.user
        dslamcommands = self.queryset

        dslam_id = self.request.query_params.get('dslam', None)
        limit_row = self.request.query_params.get('limit_row', None)
        command_type_id = self.request.query_params.get('command_type_id', None)
        command_type_name = self.request.query_params.get('command_type', None)
        if command_type_id:
            dslamcommands = dslamcommands.filter(command__id=command_type_id)
        if command_type_name:
            dslamcommands = dslamcommands.filter(command__text=command_type_name)
        else:
            query = """SELECT id FROM
            (SELECT *,row_number() OVER(PARTITION BY dslam_id,command_id ORDER BY created_at DESC) as rnk FROM dslam_dslamcommand )
            as d WHERE rnk = 1"""
            dslamcommands = dslamcommands.extra(where=["id in (%s)" % query])

        try:
            dslam = DSLAM.objects.get(id=dslam_id)
            if limit_row:
                dslamcommands = dslamcommands.filter(dslam=dslam)[:int(limit_row)]
            else:
                dslamcommands = dslamcommands.filter(dslam=dslam)
            return dslamcommands
        except:
            return []


class BulkCommand(views.APIView):
    def get_permissions(self):
        return (permissions.IsAuthenticated(),)

    def post(self, request, format=None):
        user = request.user
        data = request.data
        commands = data.get('commands')
        command_objs = []
        for command in commands:
            command_dict = dict(Command.objects.filter(id=command.get('command_id')).values('id', 'text', 'type').first())
            command_dict['params'] = command.get('params')
            command_objs.append(command_dict)
        conditions = data.get('conditions')
        title = data.get('title')
        print '======================================='
        print title
        print command_objs,
        print conditions
        print '======================================='
        result = utility.bulk_command(title, command_objs, conditions)
        return JsonResponse({'result':'Commands is running with conditions'})


class MDFDSLAMViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet):
    serializer_class = MDFDSLAMSerializer
    permission_classes = (IsAuthenticated, HasAccessToDslamPort)
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = MDFDSLAM.objects.all().order_by('identifier_key')
        telecom_center_id = self.request.query_params.get('search_telecom', None)
        telecom_mdf_id = self.request.query_params.get('search_telecom_mdf', None)
        telecom_identifier_key = self.request.query_params.get('search_identifier_key', None)
        sort_field = self.request.query_params.get('sort_field',None)

        if telecom_center_id:
            queryset = queryset.filter(telecom_center_id = telecom_center_id)

        if telecom_mdf_id:
            queryset = queryset.filter(telecom_center_mdf_id=telecom_mdf_id)

        if telecom_identifier_key:
            queryset = queryset.filter(identifier_key__istartswith=telecom_identifier_key)

        if sort_field:
            queryset = queryset.order_by(sort_field)

        return queryset

    @list_route(methods=['GET'])
    def get_free_identifier(self, request):
        data = request.query_params
        telecom_id = data.get('telecom_id')
        dslam_id = data.get('dslam_id')
        identifier_key = data.get('identifier_key')
        if not telecom_id and not dslam_id:
            return Response({'result': 'pleas send telecom_id or dslam parameter'}, status=status.HTTP_400_BAD_REQUEST)

        if dslam_id:
            dslam_ids = [dslam_id, ]
        elif telecom_id:
            telecom_obj = TelecomCenter.objects.get(id=telecom_id)
            dslam_ids = DSLAM.objects.filter(telecom_center=telecom_obj).values_list('id')

        all_identifier = set(MDFDSLAM.objects.filter(dslam_id__in=dslam_ids).values_list('identifier_key', flat=True))

        reserved_identifier = set(CustomerPort.objects.filter(telecom_center_id=telecom_id).values_list('identifier_key', flat=True))
        free_identifier = list(all_identifier - reserved_identifier)

        if identifier_key:
            free_identifier = [item for item in free_identifier if identifier_key in item]
        return HttpResponse(json.dumps(free_identifier[0:10]), content_type='application/json; charset=UTF-8')


    def create(self, request, *args, **kwargs):
        telecom_center_id = request.data.get('telecom_center_id')
        calc_faulty_port = request.data.get('calc_faulty_port')

        if not telecom_center_id:
            return Response({'result': 'telecom id is not valid'}, status=status.HTTP_400_BAD_REQUEST)

        # get all telecom dslams
        telecom_center_obj = TelecomCenter.objects.get(id=telecom_center_id)
        prefix_bukht_name = telecom_center_obj.prefix_bukht_name
        dslams = DSLAM.objects.filter(telecom_center=telecom_center_obj).order_by('dslam_number')
        print (dslams.count())
        #delete all bukht table on tc
        MDFDSLAM.objects.filter(telecom_center_id=telecom_center_id).delete()

        # Get all Bukht config TelecomCenterMDF
        telecomMDF_objs = TelecomCenterMDF.objects.filter(telecom_center=telecom_center_obj).order_by('priority', 'id')

        telecomBukht = []
        row_count = 1
        max_number = '4'

        #floor_connection_count = [[telecomMDF_obj.floor_count, telecomMDF_obj.connection_count] for telecomMDF_obj in telecomMDF_objs]
        #max_number = sum(item[0]*item[1] for item in floor_connection_count)

        for telecomMDF_obj in telecomMDF_objs:
            row_number = telecomMDF_obj.row_number
            conn_start = telecomMDF_obj.connection_start
            floor_start = telecomMDF_obj.floor_start

            conn_step = 1
            floor_step = 1

            # create floor range
            if telecomMDF_obj.floor_counting_status != "STANDARD":
                if telecomMDF_obj.floor_counting_status == "ODD":
                    if telecomMDF_obj.start_of_port % 2 == 0:
                        floor_start = floor_start + 1
                else:
                    if telecomMDF_obj.start_of_port % 2 == 1:
                        floor_start = floor_start + 1
                floor_step = 2

            floor_range = range(floor_start, telecomMDF_obj.floor_count + floor_start, floor_step)

            # create connection range
            if telecomMDF_obj.connection_counting_status != "STANDARD":
                if telecomMDF_obj.connection_counting_status == "ODD":
                    if telecomMDF_obj.connection_start % 2 == 0:
                        conn_start = telecomMDF_obj.connection_start + 1
                else:
                    if telecomMDF_obj.connection_connection_start % 2 == 1:
                        conn_start = telecomMDF_obj.connection_start + 1
                conn_step = 2

            connection_range = xrange(conn_start, conn_start + telecomMDF_obj.connection_count, conn_step)

            #create bukht table without dslam cart and port
            for floor_number in floor_range:
                for connection_number in connection_range:
                    telecomBukht.append({
                        'row_number': row_number,
                        'floor_number': floor_number,
                        'telecom_center_mdf_id': telecomMDF_obj.id,
                        'reseller': telecomMDF_obj.reseller,
                        'connection_number': connection_number,
                        'status_of_port' : telecomMDF_obj.status_of_port,
                        'identifier_key': (u'{0}-{1:0'+max_number+'}').format(unicode(prefix_bukht_name), row_count)
                        })
                    row_count += 1

        # add cart port dslam into bukht table
        telecomBukht_index = 0
        if dslams.count() > 0:
            faulty_ports = DSLAMPortFaulty.objects.filter(dslam_id__in=dslams.values_list('id', flat=True))
            for dslam in dslams:
                for dslam_cart in DSLAMCart.objects.filter(dslam=dslam).order_by('priority', 'id'):
                    slot_range = xrange(dslam_cart.cart_start, dslam_cart.cart_start + dslam_cart.cart_count)
                    port_range = xrange(dslam_cart.port_start, dslam_cart.port_start + dslam_cart.port_count)
                    try:
                        for slot in slot_range:
                            for port in port_range:
                                if calc_faulty_port:
                                    if faulty_ports.filter(slot_number=slot, port_number=port, dslam_id=dslam.id).exists():
                                        continue
                                mdf_dslam = MDFDSLAM()
                                mdf_dslam.row_number = telecomBukht[telecomBukht_index].get('row_number')
                                mdf_dslam.telecom_center_mdf_id = telecomBukht[telecomBukht_index].get('telecom_center_mdf_id')
                                mdf_dslam.floor_number = telecomBukht[telecomBukht_index].get('floor_number')
                                mdf_dslam.connection_number = telecomBukht[telecomBukht_index].get('connection_number')
                                mdf_dslam.identifier_key = telecomBukht[telecomBukht_index].get('identifier_key')
                                mdf_dslam.dslam_id = dslam.id
                                mdf_dslam.telecom_center_id = telecom_center_obj.id
                                mdf_dslam.slot_number = slot
                                mdf_dslam.port_number = port
                                mdf_dslam.status = telecomBukht[telecomBukht_index].get('status_of_port')
                                if mdf_dslam.status == 'RESELLER':
                                    reseller_obj = None
                                    reseller_obj = telecomBukht[telecomBukht_index].get('reseller')
                                    if reseller_obj:
                                        rp_obj, created = ResellerPort.objects.get_or_create(identifier_key=mdf_dslam.identifier_key, reseller=reseller_obj, telecom_center_id=mdf_dslam.telecom_center_id )
                                        mdf_dslam.reseller = reseller_obj
                                mdf_dslam.save()
                                telecomBukht_index += 1
                    except Exception as ex:
                        print ex
                        pass

        for row in telecomBukht[telecomBukht_index:]:
            mdf_dslam = MDFDSLAM()
            mdf_dslam.row_number = row.get('row_number')
            mdf_dslam.telecom_center_mdf_id = row.get('telecom_center_mdf_id')
            mdf_dslam.floor_number = row.get('floor_number')
            mdf_dslam.connection_number = row.get('connection_number')
            mdf_dslam.identifier_key = row.get('identifier_key')
            mdf_dslam.telecom_center_id = telecom_center_obj.id
            mdf_dslam.status = telecomBukht[telecomBukht_index].get('status_of_port')
            try:
                if mdf_dslam.status == 'RESELLER':
                    reseller_obj = None
                    reseller_obj = telecomBukht[telecomBukht_index].get('reseller')
                    if reseller_obj:
                        rp_obj, created = ResellerPort.objects.get_or_create(identifier_key=mdf_dslam.identifier_key, reseller=reseller_obj, telecom_center_id=mdf_dslam.telecom_center_id )
                        mdf_dslam.reseller = reseller_obj

                mdf_dslam.save()
            except Exception as ex:
                print ex

        return Response({'result': 'Created mdf dslam'}, status=status.HTTP_201_CREATED)


    @list_route(methods=['GET'])
    def download(self, request):
        def stream():
            buffer_ = StringIO.StringIO()
            writer = csv.writer(buffer_)
            writer.writerow(['row number', 'floor number', 'connection number', 'card number', 'port nummber', 'identifier key', 'status'])
            rows = MDFDSLAM.objects.filter(telecom_center_id=telecom_center_id)
            for mdf_dslam_obj in rows:
                writer.writerow([mdf_dslam_obj.row_number, mdf_dslam_obj.floor_number, mdf_dslam_obj.connection_number,\
                        mdf_dslam_obj.slot_number, mdf_dslam_obj. port_number, mdf_dslam_obj.identifier_key, mdf_dslam_obj.status])
                buffer_.seek(0)
                data = buffer_.read()
                buffer_.seek(0)
                buffer_.truncate()
                yield data
        data = request.query_params
        telecom_center_id = data.get('telecom_center_id')
        if telecom_center_id:
            response = StreamingHttpResponse(
                    stream(), content_type='text/csv'
                    )
            disposition = "attachment; filename=file.csv"
            response['Content-Disposition'] = disposition
            return response
        return None


    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        description = u'Update MDF DSLAM Status {0}: {1}'.format(instance.id, request.data)
        add_audit_log(request, 'MDFDSLAM', instance.id, 'Update MDF DSLAM', description)
        return Response(serializer.data)


class DSLAMBulkCommandResultViewSet(mixins.ListModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    serializer_class = DSLAMBulkCommandResultSerializer
    permission_classes = (IsAuthenticated, HasAccessToDslamPort)
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        user = self.request.user

        if user.type != 'ADMIN':
            return []
        queryset = DSLAMBulkCommandResult.objects.all().order_by('-created_at')
        title = self.request.query_params.get('title', None)
        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset


class DSLAMFaultyConfigViewSet(mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    serializer_class = DSLAMFaultyConfigSerializer
    permission_classes = (IsAuthenticated, )
    queryset = DSLAMFaultyConfig.objects.all()

    def get_queryset(self):
        user = self.request.user
        dslam_id = self.request.query_params.get('dslam_id', None)
        queryset = self.queryset

        if dslam_id:
            queryset = queryset.filter(dslam_id=dslam_id)
        return queryset


    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        DSLAMPortFaulty.objects.filter(dslam_faulty_config=instance.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        data = request.data
        slot_number_from = data.get('slot_number_from')
        slot_number_to = data.get('slot_number_to')
        port_number_from = data.get('port_number_from')
        port_number_to = data.get('port_number_to')
        dslam_id = data.get('dslam_id')
        faulty_configs = DSLAMFaultyConfig.objects.filter(dslam_id=dslam_id)
        for faulty_config in faulty_configs:
            if faulty_config.slot_number_from <= int(slot_number_from) and faulty_config.port_number_from <= int(port_number_from):
                if faulty_config.slot_number_to >= int(slot_number_to) and faulty_config.port_number_to >= int(port_number_to):
                    return Response({'result': 'Confilict Data'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        port_items = DSLAMPort.objects.filter(dslam_id=dslam_id).filter(slot_number__gte=slot_number_from, port_number__gte=port_number_from).\
                filter(slot_number__lte=slot_number_to).exclude(slot_number=slot_number_to, port_number__gt=port_number_to).values('dslam_id', 'slot_number', 'port_number')
        DSLAMPortFaulty.objects.filter(dslam_id=dslam_id).delete()
        dslam_faulty_config_obj = DSLAMFaultyConfig.objects.get(id=serializer.data['id'])
        for port_item in port_items:
            try:
                dslam_id = port_item['dslam_id']
                port_number = port_item['port_number']
                slot_number = port_item['slot_number']
                portfaulty = DSLAMPortFaulty()
                portfaulty.dslam_id = dslam_id
                portfaulty.dslam_faulty_config = dslam_faulty_config_obj
                portfaulty.port_number = port_number
                portfaulty.slot_number = slot_number
                portfaulty.save()
            except Exception as ex:
                print ex
                pass

        description = u'Add DSLAM Faulty Config {0}'.format(serializer.data['dslam_id'])
        add_audit_log(request, 'DSLAMFaultyConfig', serializer.data['id'], 'Add DSLAM Faulty Config', description)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data
        slot_number_from = data.get('slot_number_from')
        slot_number_to = data.get('slot_number_to')
        port_number_from = data.get('port_number_from')
        port_number_to = data.get('port_number_to')
        dslam_id = data.get('dslam_id')

        faulty_configs = DSLAMFaultyConfig.objects.filter(dslam_id=dslam_id).exclude(id=instance.pk)
        for faulty_config in faulty_configs:
            if faulty_config.slot_number_from <= int(slot_number_from) and faulty_config.port_number_from <= int(port_number_from):
                if faulty_config.slot_number_to >= int(slot_number_to) and faulty_config.port_number_to >= int(port_number_to):
                    return Response({'result': 'Confilict Data'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        port_items = DSLAMPort.objects.filter(dslam_id=dslam_id).filter(slot_number__gte=slot_number_from, port_number__gte=port_number_from).\
                filter(slot_number__lte=slot_number_to).exclude(slot_number=slot_number_to, port_number__gt=port_number_to).values('dslam_id', 'slot_number', 'port_number')

        DSLAMPortFaulty.objects.filter(dslam_faulty_config=instance).delete()
        dslam_faulty_config_obj = DSLAMFaultyConfig.objects.get(id=instance.id)
        for port_item in port_items:
            try:
                dslam_id = port_item['dslam_id']
                port_number = port_item['port_number']
                slot_number = port_item['slot_number']
                portfaulty = DSLAMPortFaulty()
                portfaulty.dslam_id = dslam_id
                portfaulty.dslam_faulty_config = dslam_faulty_config_obj
                portfaulty.port_number = port_number
                portfaulty.slot_number = slot_number
                portfaulty.save()
            except:
                pass

        description = u'Update DSLAM Falty Config {0}, params: {1}'.format(instance.id, request.data)
        add_audit_log(request, 'DSLAMFaltyConfig', instance.id, 'Update DSLAM Falty Config', description)
        return Response(serializer.data)


class DSLAMPortFaultyViewSet(mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    serializer_class = DSLAMPortFaultySerializer
    permission_classes = (IsAuthenticated, )
    queryset = DSLAMPortFaulty.objects.all()

    def get_queryset(self):
        user = self.request.user
        dslam_id = self.request.query_params.get('dslam_id', None)
        queryset = self.queryset
        if dslam_id:
            queryset = queryset.filter(dslam_id=dslam_id).order_by('slot_number', 'port_number')
        return queryset


class QuickSearchView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(),)

    def get(self, request, format=None):
        user = request.user
        value = request.query_params['value']

        dslam_objs = DSLAM.objects.all()
        port_objs = DSLAMPort.objects.all()
        mdf_dslam_objs = MDFDSLAM.objects.all()

        reseller_identifier_keys = None

        ports = []
        dslams = []

        if value:
            # search port
            user_ports = []
            mac_ports = []

            identifier_keys = list(CustomerPort.objects.filter(username__istartswith=value).values_list('identifier_key', flat=True))
            mdf_dslam_objs = mdf_dslam_objs.filter(identifier_key__in=identifier_keys)

            if user.type == 'RESELLER':
                reseller = user.reseller
                reseller_identifier_keys = ResellerPort.objects.filter(reseller=reseller).values_list('identifier_key', flat=True)
                mdf_dslam_ports = mdf_dslam_objs.filter(identifier_key__in=reseller_identifier_keys).values('dslam_id', 'slot_number', 'port_number')
                dslam_ids = set(map(lambda dslam: dslam.get('dslam_id'), mdf_dslam_ports))
                dslam_objs = dslam_objs.filter(id__in=dslam_ids).filter(Q(ip=value) | Q(name__icontains=value) | Q(hostname__icontains=value)) | Q(fqdn__icontains=value)
            else:
                dslam_objs = dslam_objs.filter(Q(ip=value) | Q(name__icontains=value) | Q(hostname__icontains=value) | Q(fqdn__icontains=value))
                mdf_dslam_ports = mdf_dslam_objs.values('dslam_id', 'slot_number', 'port_number')

            for mdf_dslam_port in mdf_dslam_ports:
                user_ports.append(port_objs.get(
                        dslam_id=mdf_dslam_port['dslam_id'],
                        slot_number=mdf_dslam_port['slot_number'],
                        port_number=mdf_dslam_port['port_number']).pk)

            if user_ports:
                port_objs = port_objs.filter(id__in=user_ports)

            mac_ports = list(DSLAMPortMac.objects.filter(mac_address__istartswith=value).values_list('port__id', flat=True))

            if mac_ports:
                port_objs = port_objs.filter(id__in=mac_ports)

            if user_ports or mac_ports:
                ports = [{'id': port.id, 'port_index': port.port_index, 'slot_number': port.slot_number, 'port_number': port.port_number, 'port_name': port.port_name, 'dslam_id': port.dslam.id, 'dslam_name': port.dslam.name, 'hostname': port.dslam.hostname} for port in port_objs]
                # end search port

            dslams =[{'id': dslam.id, 'name': dslam.name, 'hostname': dslam.hostname, 'ip': dslam.ip, 'type': dslam.dslam_type.name} for dslam in dslam_objs]
        return Response({'result': {'dslams': dslams, 'ports': ports}})


class RegisterPortAPIView(views.APIView):
    """
    "port":{
        "telecom_center_name": "string",
        "fqdn": "string",
        "card_number": "string",
        "port_number": "string"
    },
    "status": "RESELLER",
    "identifier_key":"string",
    "reseller": {
          "name": "string",
    },
    "subscriber":{
          "username": "string",
    }
    """
    def get_permissions(self):
        return (permissions.IsAuthenticated(),)

    def post(self, request, format=None):
        user = request.user
        data = request.data
        print data
        reseller_data = data.get('reseller')
        customer_data = data.get('subscriber')
        mdf_status = data.get('status')
        if not mdf_status:
            mdf_status = 'BUSY'

        identifier_key = data.get('identifier_key')
        if not identifier_key:
            identifier_key = str(time.time())
        port_data = data.get('port')

        try:
            #dslam_obj = DSLAM.objects.get(name=port_data.get('dslam_name'), telecom_center__name=port_data.get('telecom_center_name'))
            dslam_obj = DSLAM.objects.get(fqdn=port_data.get('fqdn'))

            telecom_mdf_obj = TelecomCenterMDF.objects.filter(telecom_center_id = dslam_obj.telecom_center.id)
            if telecom_mdf_obj:
                telecom_mdf_obj = telecom_mdf_obj.first()

            mdf_dslam_obj, mdf_dslam__updated = MDFDSLAM.objects.update_or_create(
                    telecom_center_id=dslam_obj.telecom_center.id, telecom_center_mdf_id = telecom_mdf_obj.id, #### Check this whole line
                    row_number=0, floor_number=0, connection_number=0, ##### Check this whole line
                    dslam_id=dslam_obj.id, slot_number=port_data.get('card_number'), port_number=port_data.get('port_number'),
                    defaults={'status': mdf_status, 'identifier_key': identifier_key})
            #if mdf_dslam.status != 'FREE':
            #    return JsonResponse(
            #            {'result': 'port status is {0}'.format(mdf_dslam.status), 'id': -1}
            #            )
            #else:
            #    mdf_dslam.status = 'RESELLER'
            #    mdf_dslam.save()
            #identifier_key = mdf_dslam.identifier_key
        except ObjectDoesNotExist as ex:
            return JsonResponse({'result': str(ex), 'id': -1})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
	    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]   
            return JsonResponse({'result': 'Error is {0}'.format(ex), 'Line': str( dslam_obj.telecom_center.id), 'testRes':serialize('json', telecom_mdf_obj)})

        try:
          reseller_obj, reseller_created = Reseller.objects.get_or_create(name=reseller_data.get('name'))
          print 'reseller', reseller_obj

          customer_obj, customer_updated = CustomerPort.objects.update_or_create(
                      username=customer_data.get('username'),
                      defaults={'identifier_key': identifier_key, 'telecom_center_id': mdf_dslam_obj.telecom_center_id}
                  )

          rp = ResellerPort()
          rp.identifier_key = identifier_key
          rp.status = 'ENABLE'
          rp.dslam_id = dslam_obj.id
          rp.dslam_slot = port_data.get('card_number')
          rp.dslam_port = port_data.get('port_number')
          rp.reseller = reseller_obj
          rp.telecom_center_id = mdf_dslam_obj.telecom_center_id
          rp.save()

          vlan_objs = Vlan.objects.filter(reseller=reseller_obj)
          print 'vlan_objs ->', vlan_objs

          port_indexes =[{'slot_number': port_data.get('card_number'), 'port_number':port_data.get('port_number')}]
          params = {
                  "type":"dslamport",
                  "is_queue":False,
                  "vlan_id": vlan_objs[0].vlan_id,
                  "vlan_name": vlan_objs[0].vlan_name,
                  "dslam_id": dslam_obj.id,
                  "port_indexes": port_indexes,
                  "username": customer_data.get('username'),
                  }
      
          if vlan_objs.count() > 0:
              port_obj = DSLAMPort.objects.get(dslam=dslam_obj, slot_number=port_data.get('card_number'), port_number=port_data.get('port_number'))
              port_vlan_obj = DSLAMPortVlan()
              port_vlan_obj.vlan = vlan_objs.first()
              port_vlan_obj = port_obj
              port_vlan_obj.save()

          return JsonResponse({'result':'Port is registered', 'id': 201}, status=status.HTTP_201_CREATED)
        except Exception as ex:
          exc_type, exc_obj, exc_tb = sys.exc_info()
	  fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]   
          #return JsonResponse({'result': 'Error is {0}'.format(ex), 'Line': str(exc_tb.tb_lineno)})
          return JsonResponse({'result': str('an error occurred. please try again')}, status=status.HTTP_202_ACCEPTED)




class showPort():
    dslamName = ''
    cammandName = ''
    slotPort = ''
    link = ''
    payloadrate = 0
    actualrate = 0
    attainablerate = 0
    noisemargin = 0
    attenuation= 0
    userProfile = ''

class DslanInfo():
    type = ''
    dslam = ''
    telnetPort = 23
    userName = ''
    password = ''
    access = ''
    card = ''
    port = ''
    command = ''
    terminalDelay =''
    requestTimeOut = ''
    userProfile = ''

class fInfo():
    Date = ''
    cardInfo = ''
    OP_State = ''
    Standard = ''
    Latency = ''
    Stream_SNR_Margin = ''
    Rate =''
    Stream_attenuation = ''
    Tx_power = ''
    Remote_vendor_ID = ''
    Power_management_state = ''
    Remote_vendor_version_ID = ''
    Loss_of_power = ''
    Errored_frames = ''
    Loss_of_signal = ''
    Error_seconds = ''
    Loss_by_HEC_collision = ''
    Forward_correct = ''
    Uncorrect = ''
    Attainable_rate = ''
    Interleaved_Delay = ''
    Remote_loss_of_link = ''


class RunCommandAPIView(views.APIView):
    def get_permissions(self):
        return (permissions.IsAuthenticated(),)

    def post(self, request, format=None):
      try:
        user = request.user
        data = request.data
        s = []
        command = data.get('command', None)
        dslam_id = DSLAM.objects.get(fqdn=request.data.get('fqdn')).id
	dslam_ip =DSLAM.objects.get(fqdn=request.data.get('fqdn')).id
	userProfile = DSLAMPort.objects.get(port_number = request.data.get('params').get('port_conditions').get('port_number'), slot_number = request.data.get('params').get('port_conditions').get('slot_number'), dslam_id = dslam_id).line_profile
        params = data.get('params', None)
        try:
            dslam_obj = DSLAM.objects.get(id=dslam_id)
  	    fiber = DslanInfo()
            fiber.type = 'Fiberhome'
            fiber.dslam = dslam_obj.ip
            fiber.telnetPort = 23
            fiber.userName = dslam_obj.telnet_username
            fiber.password = dslam_obj.telnet_password
            fiber.access = dslam_obj.access_name
            fiber.card = request.data.get('params').get('port_conditions').get('slot_number')
            fiber.port = request.data.get('params').get('port_conditions').get('port_number')
            fiber.terminalDelay = '300'
            fiber.requestTimeOut = '15000'
#---------------------------------------------------Fiberhome2200---------------------------------------------------
	    if(dslam_obj.dslam_type_id == 4):
               if(command  == 'selt'):
                 return JsonResponse({'res': 'this command is not supported by this dslam' })
	       if(command== 'show linerate' or command== 'showPort' ):
	         fiber.command = 'showPort'
	       if(command== 'profile adsl show' or  command== 'showProfiles'):
	         fiber.command = 'showProfiles'
	       url = 'http://5.202.129.88:9095/api/Telnet/telnet'
               data = "{'type':'Fiberhome','dslam':'%s','telnetPort':'23','userName':'%s','password':'%s','access':'%s','card':'%s','port':'%s','command':'%s','terminalDelay':'600','requestTimeOut':'15000'}"  % (fiber.dslam ,fiber.userName, fiber.password,fiber.access,fiber.card,fiber.port,fiber.command)
               fhresponse = requests.post(url, data=data, headers={"Content-Type": "application/json"})
               sid=fhresponse.json()
	       res = sid.split("\n\r")
	       if(command== 'show linerate' or command== 'showPort' ):
		 fhome = fInfo()
		 fhome.Date = sid.split("\n\r")[0]  
		 portInfo = [int(c) for c in res[3].split() if c.isdigit()]
	         return JsonResponse({'current_userProfile':userProfile ,
                        	      'dslamName/cammandName': dslam_obj.name + '/' + command,
                                      'date':res[0].split(":")[1] + res[0].split(":")[2]+ ':' + res[0].split(":")[3],
				      'slot/port' : str(portInfo[1]) + '-' + str(portInfo[2]),
				      #'OP_State' : res[4].split(":")[1],
				      #'Standard' : res[5].split(":")[1],
				      #'Latency' : res[6].split(":")[1],
				      'noisemarginDown' : res[7].split(":")[1].split("/")[0],
				      'noisemarginUp' : res[7].split(":")[1].split("/")[1].split(" ")[0],
				      'payloadrateDown' : res[8].split(":")[1].split("/")[0],
				      'payloadrateUp' : res[8].split(":")[1].split("/")[1].split(" ")[0],
				      'attenuationDown' : res[9].split(":")[1].split("/")[0],
				      'attenuationUp' : res[9].split(":")[1].split("/")[1].split(" ")[0],
				      #'Tx power(D/U)' : res[10].split(":")[1].split("/")[0],	
				      #'Tx power(D/U)' : res[10].split(":")[1].split("/")[1].split(" ")[0],	
				      #'Remote vendor ID' : res[11].split(":")[1],
				      #'Power management state' : res[12].split(":")[1],
				      #'Remote vendor version ID' : res[13].split(":")[1],
				      #'Loss of power(D)' : res[14].split(":")[1].split("/")[0],
				      #'Loss of power(U)' : res[14].split(":")[1].split("/")[1].split(" ")[0],
				      #'Loss of signal(D)' : res[15].split(":")[1].split("/")[0],
				      #'Loss of signal(U)' : res[15].split(":")[1].split("/")[1].split(" ")[0],
				      #'Error seconds(D)' : res[16].split(":")[1].split("/")[0],
				      #'Error seconds(U)' : res[16].split(":")[1].split("/")[1].split(" ")[0],
				      #'Loss by HEC collision(D)' : res[17].split(":")[1].split("/")[0],
				      #'Loss by HEC collision(U)' : res[17].split(":")[1].split("/")[1].split(" ")[0],
				      #'Forward correct(D)' : res[18].split(":")[1].split("/")[0],
				      #'Forward correct(U)' : res[18].split(":")[1].split("/")[1],
				      #'Uncorrect(D)' : res[19].split(":")[1].split("/")[0],
				      #'Uncorrect(U)' : res[19].split(":")[1].split("/")[1],
				      'attainablerateDown' : res[20].split(":")[1].split("/")[0],
				      'attainablerateUp' : res[20].split(":")[1].split("/")[1],
				      #'Interleaved Delay(D) ' : res[21].split(":")[1].split("/")[0],
				      #'Interleaved Delay(U) ' : res[21].split(":")[1].split("/")[1],
				      #'Remote loss of link' : res[22].split(":")[1],
											})
                 return JsonResponse({'current_userProfile':userProfile ,'response':sid.split("\n\r")  })
               #elif(command== 'profile adsl show' or  command== 'showProfiles'):
                #return JsonResponse({'current_userProfile':userProfile ,'response':sid.split("\n\r")  })
               else:
                return JsonResponse({'current_userProfile':userProfile ,'response':sid.split("\n\r")  })

#---------------------------------------------------Fiberhome5006---------------------------------------------------
	    elif(dslam_obj.dslam_type_id == 5):
               if(command  == 'selt'):
                 return JsonResponse({'res': 'this command is not supported by this dslam' })
	       if(command== 'show linerate' or command== 'showPort' ):
	         fiber.command = 'showPort'
	       if(command== 'profile adsl show' or  command== 'showProfiles'):
	         fiber.command = 'showProfiles'
	       url = 'http://5.202.129.88:9095/api/Telnet/telnet'
               data = "{'type':'FiberhomeAN5006','dslam':'%s','telnetPort':'23','userName':'%s','password':'%s','access':'%s','card':'%s','port':'%s','command':'%s','terminalDelay':'600','requestTimeOut':'15000'}"  % (fiber.dslam ,fiber.userName, fiber.password,fiber.access,fiber.card,fiber.port,fiber.command)
               fhresponse = requests.post(url, data=data, headers={"Content-Type": "application/json"})
               sid=fhresponse.json()
	       res = sid.split("\n\r")
               return JsonResponse({'current_userProfile':userProfile ,'response':sid.split("\r\n")  })

#---------------------------------------------------zyxel---------------------------------------------------
            description = u'Run Command {0} on DSLAM {1}'.format(
                    command,
                    dslam_obj.name,
                    )
        except Exception as ex:
	    exc_type, exc_obj, exc_tb = sys.exc_info()
	    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #return Response({'result': str(ex),'Line': str(exc_tb.tb_lineno)}, status=status.HTTP_400_BAD_REQUEST)
	    return JsonResponse({'result': str('an error occurred. please try again')})

        
        if(command== 'show linerate' or command== 'showPort' ):
	         command = 'show linerate'
	if(command== 'profile adsl show' or  command== 'showProfiles'):
	         command = 'profile adsl show'

        if not command:
            return Response({'result': 'Command does not exits'}, status=status.HTTP_400_BAD_REQUEST)
        params["username"] = user.username
        result = utility.dslam_port_run_command(dslam_obj.pk, command, params)
        if result:
            if 'Busy' in result:
                return Response({'result': result}, status=status.HTTP_400_BAD_REQUEST)
            else:
                description = u'Run Command {0} on DSLAM {1}'.format(
                    command,
                    dslam_obj.name)

                add_audit_log(request, 'DSLAMCommand', None, 'Run Command On DSLAM Port', description)
	if(command == "show linerate"):
	   sp = showPort()
	   result = result['result'].split("\r\n")
	   sp.dslamNameAndcammandName = result[1]
	   sp.slotPort = result[2].split(",")[0].split("=")[1]
	   sp.link = result[3].replace(" ", "").split("=")[1]
	   payloadrate = result[6].split("=")[1]
	   sp.payloadrate = [int(s) for s in payloadrate.split() if s.isdigit()]
	   actualrate = result[7].split("=")[1]
	   sp.actualrate = [int(c) for c in actualrate.split() if c.isdigit()]
	   attainablerate = result[8].split("=")[1]
	   sp.attainablerate = [int(c) for c in attainablerate.split() if c.isdigit()]
	   noisemargin = result[9].split("=")[1]
	   sp.noisemargin =re.findall(r"[-+]?\d*\.\d+|\d+", noisemargin)
	   attenuation= result[10].split("=")[1]
	   sp.attenuation =  re.findall(r"[-+]?\d*\.\d+|\d+", attenuation)
           return JsonResponse({  
                        	  'dslamName/cammandName': sp.dslamNameAndcammandName,
				  'slot/Port' : sp.slotPort,
				  'link' : sp.link,
				  'payloadrateUp' : sp.payloadrate[0],
				  'payloadrateDown' : sp.payloadrate[1],
				  'actualrateUp' : sp.actualrate[0],
				  'actualrateDown' : sp.actualrate[1],
				  'attainablerateUp' : sp.attainablerate[0],
				  'attainablerateDown' : sp.attainablerate[1],
				  'noisemarginUp' : sp.noisemargin[0],
				  'noisemarginDown' : sp.noisemargin[1],
				  'attenuationUp' : sp.attenuation[0],
				  'attenuationDown' : sp.attenuation[1],
				  'current_userProfile':userProfile
				   }, status=status.HTTP_201_CREATED)
	elif (command == "show lineinfo"):
	   return JsonResponse({'current_userProfile':userProfile ,'response':result['result'].split("\r\n")})
	elif (command == "selt"):
	   return JsonResponse({'current_userProfile':userProfile ,'response':result})     
	else:
	   return JsonResponse({'response':result['result']})   
      except Exception as ex:
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
        #return JsonResponse({'result': str(ex),'Line': str(exc_tb.tb_lineno)}, status=status.HTTP_202_ACCEPTED)
        return JsonResponse({'result': str('an error occurred. please try again')}, status=status.HTTP_202_ACCEPTED)






