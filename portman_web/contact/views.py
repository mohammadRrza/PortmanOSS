import json
import sys, os
from datetime import time

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from django.db import connection
from rest_framework import status, views, mixins, viewsets, permissions
from contact.models import Order, Province, City, TelecommunicationCenters, PortmapState, FarzaneganTDLTE, \
    FarzaneganProviderData
from django.http import JsonResponse, HttpResponse
from rest_framework.permissions import IsAuthenticated
from contact.serializers import OrderSerializer, DDRPageSerializer, FarzaneganSerializer, GetNotesSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.core.serializers import serialize
from classes.mellat_bank_scrapping import get_captcha


from classes.farzanegan_selenium import farzanegan_scrapping
# from portman_web.classes.farzanegan_selenium import farzanegan_scrapping
from contact.models import PishgamanNote


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
            _fields = ['username', 'ranjePhoneNumber', 'slot_number', 'port_number', 'telecomCenter_info',
                       'telco_row', 'telco_column', 'telco_connection', 'fqdn', 'port_status_info']
            return OrderSerializer(request=self.request, remove_fields=_fields, *args, **kwargs)
        else:
            print(self.request.user.type)
            _fields = ['username', 'ranjePhoneNumber', 'slot_number', 'port_number', 'telecomCenter_info',
                       'telco_row', 'telco_column', 'telco_connection', 'fqdn', 'port_status_info']
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
        telecom_id = self.request.query_params.get('telecom_id')
        port_status_id = self.request.query_params.get('port_status_id')

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

        if telecom_id:
            queryset = queryset.filter(telecom_id=telecom_id)

        if port_status_id:
            queryset = queryset.filter(status_id=port_status_id)

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
                provinces = Province.objects.filter(provinceName__icontains=province_name).values().order_by(
                    'provinceName')[:10]
                return JsonResponse({"result": list(provinces)})
            provinces = Province.objects.all().values().order_by('provinceName')[:10]
            return JsonResponse({"result": list(provinces)})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})


class GetCitiesByProvinceIdAPIView(views.APIView):
    def get(self, request, format=None):
        try:
            province_id = request.query_params.get('province_id')
            city_name = request.query_params.get('city_name')

            if province_id and city_name:
                Cities = City.objects.filter(provinceId=province_id, cityName__icontains=city_name).values().order_by(
                    'cityName')[:10]
                return JsonResponse({"result": list(Cities)})
            Cities = City.objects.all().values().order_by('cityName')[:10]
            return JsonResponse({"result": list(Cities)})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})


class GetTelecomsByCityIdAPIView(views.APIView):
    def get(self, request, format=None):
        try:
            city_id = request.query_params.get('city_id')
            telecom_name = request.query_params.get('telecom_name')

            if city_id and telecom_name:
                telecoms = TelecommunicationCenters.objects.filter(city_id=city_id,
                                                                   name__icontains=telecom_name).values().order_by(
                    'name')[:10]
                return JsonResponse({"result": list(telecoms)})
            telecoms = TelecommunicationCenters.objects.all().values().order_by('name')[:10]
            return JsonResponse({"result": list(telecoms)})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})


class GetPortsStatus(views.APIView):
    def get(self, request, format=None):
        try:
            statuses = PortmapState.objects.all().values().order_by('description')[:10]
            return JsonResponse({"result": list(statuses)})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})


class SearchPorts(views.APIView):
    def get(self, request, format=None):
        try:
            province_id = request.query_params.get('province_id')
            city_id = request.query_params.get('city_id')
            telecom_id = request.query_params.get('telecom_id')
            port_status_id = request.query_params.get('port_status_id')
            """if province_id:
                query = 'select * from contact_order o INNER JOIN contact_telecommunicationcenters tc on tc."id" = o.telecom_id INNER JOIN contact_city ci on ci."id" = tc.city_id INNER JOIN contact_province cp on cp."id" = ci.province_id WHERE cp."id" = {0} limit 100'.format(province_id)
                cursor = connection.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                print(rows)
                return JsonResponse({"result": rows})
            if city_id:
                ports = Order.objects.select_related('telecom__city').filter(city_id=city_id)"""
            if telecom_id and port_status_id == "":
                ports = Order.objects.filter(telecom_id=telecom_id).values()
            if port_status_id and telecom_id:
                ports = Order.objects.filter(telecom_id=int(telecom_id), status_id=int(port_status_id)).values()
            return JsonResponse({"result": list(ports)})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})


class UpdateStatusPorts(views.APIView):
    def post(self, request, format=None):
        try:
            data = request.data
            username = data.get('username', None)
            new_port_status_id = data.get('port_status_id', None)
            order = Order.objects.get(username=username)
            order.status_id = new_port_status_id
            order.save()
            return JsonResponse(
                {"username": str(order.username), "status": str(order.status), "telecom": str(order.telecom)})

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})


class UpdateStatusPorts2(views.APIView):
    def post(self, request, format=None):
        try:
            data = request.data
            username = data.get('username', None)
            ranjePhoneNumber = data.get('ranjePhoneNumber', None)
            old_port_status_id = data.get('old_port_status_id', None)
            new_port_status_id = data.get('new_port_status_id', None)
            telecom_id = data.get('telecom_id', None)
            telco_row = data.get('old_telco_row', None)
            telco_column = data.get('old_telco_column', None)
            telco_connection = data.get('old_telco_connection', None)
            new_telco_row = data.get('new_telco_row', None)
            new_telco_column = data.get('new_telco_column', None)
            new_telco_connection = data.get('new_telco_connection', None)
            try:
                old_order = Order.objects.get(telecom_id=telecom_id, telco_row=telco_row, telco_column=telco_column,
                                              telco_connection=telco_connection)
            except ObjectDoesNotExist as ex:
                return JsonResponse({"Message": "Old Bukht is not available in this telecommunication center."},
                                    status=500)
            old_order.status_id = old_port_status_id
            old_order.username = 'NULL'
            old_order.ranjePhoneNumber = 'NULL'
            try:
                new_order = Order.objects.get(telecom_id=telecom_id, telco_row=new_telco_row,
                                              telco_column=new_telco_column,
                                              telco_connection=new_telco_connection)
            except ObjectDoesNotExist as ex:
                return JsonResponse({"Message": "New Bukht is not available in this telecommunication center."},
                                    status=500)
            new_order.status_id = new_port_status_id
            new_order.username = username
            new_order.ranjePhoneNumber = ranjePhoneNumber
            old_order.save()
            new_order.save()
            return JsonResponse({"username": str(new_order.username), "status": str(new_order.status),
                                 "telecom": str(new_order.telecom), "telecom_id": str(new_order.telecom_id)},
                                status=200)

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)}, status=500)


class GetOrdrPortInfo(views.APIView):
    def get(self, request, format=None):
        try:
            username = request.query_params.get('username')
            order_port = Order.objects.get(username=username)

            return JsonResponse({"username": str(order_port.username), "status": str(order_port.status),
                                 "telecom": str(order_port.telecom), "telecom_id": str(order_port.telecom_id)})

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})


class GetCaptchaAPIView(views.APIView):
    def get(self, request, format=None):
        try:
            get_captcha()
            with open('/home/sajad/Project/portmanv3/portman_web/classes/screenshot.png', 'rb') as f:
                return HttpResponse(f.read(), content_type='image/png')

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})


class GetCitiesFromPratakAPIView(views.APIView):

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def get(self, request, format=None):
        try:
            table_name = '"partak_telecom"'
            url = 'https://my.pishgaman.net/api/pte/getProvinceList'
            url_response = requests.get(url, headers={"Content-Type": "application/json"})
            response = url_response.json()
            print(response['ProvinceList'])
            for item in response['ProvinceList']:
                p_url = 'https://my.pishgaman.net/api/pte/getCityList?ProvinceID={}'.format(item['ProvinceID'])
                p_url_response = requests.get(p_url, headers={"Content-Type": "application/json"})
                p_response = p_url_response.json()
                for item2 in p_response['CityList']:
                    p_url = 'https://my.pishgaman.net/api/pte/getMdfList?CityID={}'.format(item2['CityID'])
                    p_url_response = requests.get(p_url, headers={"Content-Type": "application/json"})
                    p_response = p_url_response.json()
                    for item3 in p_response['MdfList']:
                        query = "INSERT INTO public.{} VALUES ({}, '{}', '{}', '{}', '{}', '{}');".format(table_name,
                                                                                                          item[
                                                                                                              'ProvinceID'],
                                                                                                          item[
                                                                                                              'ProvinceName'],
                                                                                                          item2[
                                                                                                              'CityID'],
                                                                                                          item2[
                                                                                                              'CityName'],
                                                                                                          item3[
                                                                                                              'MdfID'],
                                                                                                          item3[
                                                                                                              'MdfName'])
                        cursor = connection.cursor()
                        cursor.execute(query)

            # url = 'https://my.pishgaman.net/api/pte/getCityList?ProvinceID={0}'.format(username)
            # url_response = requests.get(url, headers={"Content-Type": "application/json"})
            # response = url_response.json()
            # print(response)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as ex:
            print(ex)
            return Response(str(ex), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FarzaneganScrappingAPIView(views.APIView):
    def post(self, request, format=None):
        data = request.data
        print(data)
        username = data['username']
        password = data['password']
        owner_username = data['owner_username']
        try:
            result = "" #farzanegan_scrapping(username, password, owner_username)
            if result is None:
                return Response({'result': 'Please try again!'})
            return Response({'result': result})

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})


class DDRPageViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = DDRPageSerializer
    pagination_class = LargeResultsSetPagination
    queryset = FarzaneganTDLTE.objects.all()

    def get_serializer(self, *args, **kwargs):
        if self.request.user.is_superuser:
            print(self.request.user.type)
            return DDRPageSerializer(request=self.request, *args, **kwargs)
        elif self.request.user.type == 'SUPPORT':
            print(self.request.user.type)
            _fields = ['date_key', 'provider', 'customer_msisdn', 'total_data_volume_income']
            return DDRPageSerializer(request=self.request, remove_fields=_fields, *args, **kwargs)
        else:
            print(self.request.user.type)
            _fields = ['date_key', 'provider', 'customer_msisdn', 'total_data_volume_income']

            return DDRPageSerializer(request=self.request, remove_fields=_fields, *args, **kwargs)

    @action(methods=['GET'], detail=False)
    def current(self, request):
        serializer = DDRPageSerializer(request.user, request=request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user


class FarzaneganViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = FarzaneganTDLTE.objects.all().order_by('-date_key')
    permission_classes = (IsAuthenticated,)
    serializer_class = FarzaneganSerializer

    def get_queryset(self):
        queryset = self.queryset
        owner_username = self.request.query_params.get('owner_username', None)
        print(owner_username)
        if owner_username:
            print(owner_username)
            queryset = queryset.filter(owner_username=owner_username)

        return queryset


class FarzaneganExportExcelAPIView(views.APIView):
    def get(self, request, format=None):
        try:
            owner_username = request.GET.get('owner_username', None)
            print(owner_username)
            farzanegan_tdlte = FarzaneganTDLTE.objects.filter(owner_username=owner_username).values()
            return Response({'result': farzanegan_tdlte})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})


class FarzaneganProviderDataAPIView(views.APIView):
    def get(self, request, format=None):
        try:
            owner_username = request.GET.get('owner_username', None)
            print(owner_username)
            provider = FarzaneganTDLTE.objects.filter(owner_username=owner_username).first()
            farzanegan_provider_data = FarzaneganProviderData.objects.filter(provider_id=provider.provider_id).order_by(
                '-created').values().first()
            print(farzanegan_provider_data)
            return Response({'result': farzanegan_provider_data})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})


class GetPartakProvincesAPIView(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def get(self, request, format=None):
        try:
            url = 'https://my.pishgaman.net/api/pte/getProvinceList'
            url_response = requests.get(url, headers={"Content-Type": "application/json"})
            response = url_response.json()
            print(response)
            return Response(response, status=status.HTTP_200_OK)

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return JsonResponse({'row': str(ex) + '////' + str(exc_tb.tb_lineno)})


class GetPartakCitiesByProvinceIdAPIView(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def get(self, request, format=None):
        try:
            province_id = request.GET.get('province_id', None)
            url = 'https://my.pishgaman.net/api/pte/getCityList?ProvinceID={}'.format(province_id)
            url_response = requests.get(url, headers={"Content-Type": "application/json"})
            response = url_response.json()
            print(url_response)
            return Response(response, status=status.HTTP_200_OK)

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return JsonResponse({'row': str(ex) + '////' + str(exc_tb.tb_lineno)})


class GetPartakTelecomsByCityIdAPIView(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def get(self, request, format=None):
        try:
            city_id = request.GET.get('city_id', None)
            url = 'https://my.pishgaman.net/api/pte/getMdfList?CityID={}'.format(city_id)
            url_response = requests.get(url, headers={"Content-Type": "application/json"})
            response = url_response.json()
            print(response)
            return Response(response, status=status.HTTP_200_OK)

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return JsonResponse({'row': str(ex) + '////' + str(exc_tb.tb_lineno)})


class GetPartakDslamListByTelecomIdAPIView(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def get(self, request, format=None):
        try:
            mdf_id = request.GET.get('mdf_id', None)
            url = 'https://my.pishgaman.net/api/pte/getDslamList?MdfID={}'.format(mdf_id)
            url_response = requests.get(url, headers={"Content-Type": "application/json"})
            response = url_response.json()
            print(response)
            return Response(response, status=status.HTTP_200_OK)

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return JsonResponse({'row': str(ex) + '////' + str(exc_tb.tb_lineno)})


class UpdatePartakFqdnAPIView(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def get(self, request, format=None):
        try:
            mdf_id = request.GET.get('mdf_id', None)
            slat = request.GET.get('slat', None)
            fqdn = request.GET.get('fqdn', None)
            url = 'https://my.pishgaman.net/api/pte/updateFqdn?MdfID={}&Slat={}&NewFQDN={}'.format(mdf_id, slat, fqdn)
            url_response = requests.get(url, headers={"Content-Type": "application/json"})
            response = url_response.json()
            print(response)
            return Response(response, status=status.HTTP_200_OK)

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return JsonResponse({'row': str(ex) + '////' + str(exc_tb.tb_lineno)})


class SaveNoteAPIView(views.APIView):
    def post(self, request):
        try:
            data = request.data
            province = data.get('province')
            city = data.get('city')
            telecom_center = data.get('telecom_center')
            problem_desc = data.get('problem_description')
            username = data.get('username')
            PishgamanNote.objects.create(province=province, city=city, telecom_center=telecom_center,
                                         problem_desc=problem_desc, username=username)
            return Response({"result": "New Note Successfully Added."})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return JsonResponse({'row': str(ex) + '////' + str(exc_tb.tb_lineno)})


class GetNotesViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    queryset = PishgamanNote.objects.all().order_by(
                '-register_time')
    serializer_class = GetNotesSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        queryset = self.queryset

        return queryset
