import sys, os
from datetime import time
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from rest_framework import status, views, mixins, viewsets, permissions
from router import utility
from router.models import Router, RouterCommand
from django.http import JsonResponse, HttpResponse
from rest_framework.permissions import IsAuthenticated
from router.serializers import RouterSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from router.serializers import RouterSerializer, RouterCommandSerializer


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = max


class RouterRunCommandAPIView(views.APIView):
    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def post(self, request):
        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            user = request.user
            data = request.data
            return JsonResponse({'Result': request.data.get('fqdn')}, status=status.HTTP_200_OK)
            s = []
            command = data.get('command', None)
            params = data.get('params', None)
            subscriber = data.get('subscriber')
            fqdn = request.data.get('fqdn')
            routerObj = Router.objects.get(fqdn=fqdn)
            result = utility.router_run_command(routerObj.pk, command, params)
            return JsonResponse({'response': result})

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return JsonResponse(
                {'result': str('an error occurred. please try again. {0}'.format(str(exc_tb.tb_lineno)))},
                status=status.HTTP_202_ACCEPTED)


class RouterViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Router.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = RouterSerializer
    pagination_class = LargeResultsSetPagination

    def get_serializer(self, *args, **kwargs):
        if self.request.user.is_superuser:
            print((self.request.user.type))
            return RouterSerializer(request=self.request, *args, **kwargs)
        elif self.request.user.type == 'SUPPORT':
            print((self.request.user.type))
            '''_fields = ['id', 'device_name', 'device_ip', 'device_fqdn']'''
            return RouterSerializer(request=self.request, *args, **kwargs)
        else:
            print((self.request.user.type))
            '''_fields = ['id', 'device_name', 'device_ip', 'device_fqdn']'''
            return RouterSerializer(request=self.request, *args, **kwargs)

    @action(methods=['GET'], detail=False)
    def current(self, request):
        serializer = RouterSerializer(request.user, request=request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        sort_field = self.request.query_params.get('sort_field', None)
        router_name = self.request.query_params.get('search_router', None)
        device_ip = self.request.query_params.get('search_ip', None)
        ip_list = self.request.query_params.get('search_ip_list', None)
        city_id = self.request.query_params.get('search_city', None)
        telecom = self.request.query_params.get('search_telecom', None)
        device_fqdn = self.request.query_params.get('search_fqdn', None)
        active = self.request.query_params.get('search_active', None)
        status = self.request.query_params.get('search_status', None)
        router_type_id = self.request.query_params.get('search_type', None)

        if router_type_id:
            queryset = queryset.filter(router_type__id=router_type_id)

        if router_name:
            queryset = queryset.filter(device_name__istartswith=router_name)

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
                queryset = queryset.filter(device_ip__istartswith=ip)

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


class RouterRunCommandAPIView(views.APIView):
    def post(self, request, format=None):
        try:
            data = request.data
            router_id = data.get('router_id')
            params = data.get('params')
            command = data.get('command')
            result = utility.router_run_command(router_id, command, params)
            if command == 'get Backup':
                return JsonResponse({'response': result})
            return JsonResponse({'response': result})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return JsonResponse({'Error': str(ex), 'Line': str(exc_tb.tb_lineno)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RouterCommandViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = RouterCommandSerializer
    permission_classes = (IsAuthenticated,)
    queryset = RouterCommand.objects.all()
    paginate_by = None
    paginate_by_param = None
    paginator = None

    def get_queryset(self):
        user = self.request.user
        RouterCommands = self.queryset

        limit_row = self.request.query_params.get('limit_row', None)
        router_type_id = self.request.query_params.get('router_type_id', None)
        router_command_description = self.request.query_params.get('command_type', None)
        router_command_text = self.request.query_params.get('command_type', None)
        try:
            if router_type_id:
                RouterCommands = RouterCommands.filter(router_type_id=router_type_id)
            if limit_row:
                RouterCommands = RouterCommands.filter(router_type_id=router_type_id)[:int(limit_row)]
            else:
                RouterCommands = RouterCommands.filter(router_type_id=router_type_id)
            return RouterCommands
        except:
            return []


path = '/opt/portmanv3/portman_core2/router_vendors/mikrotik_commands/Backups/'


class GetRouterBackupFilesNameAPIView(views.APIView):
    def post(self, request, format=None):
        try:
            router_id = request.data.get('router_id')
            router_obj = Router.objects.get(id=router_id)
            fqdn = router_obj.device_fqdn
            filenames = []
            directory = path
            for filename in os.listdir(directory):
                if filename.__contains__(fqdn):
                    filenames.append(filename)
                else:
                    continue
            return JsonResponse({'response': filenames})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})


class DownloadRouterBackupFileAPIView(views.APIView):

    def post(self, request, format=None):
        try:
            download_backup_file = request.data.get('backup_file_name')
            directory = path + download_backup_file
            f = open(directory, "r")
            print(directory)
            return JsonResponse({'response': f.read()})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})


class GetRouterBackupErrorFilesNameAPIView(views.APIView):

    def post(self, request, format=None):
        try:
            filenames = []
            directory = path
            for filename in os.listdir(directory):
                if filename.__contains__('Error'):
                    filenames.append(filename)
                else:
                    continue
            return JsonResponse({'response': filenames})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return JsonResponse({'row': str(ex) + "  // " + str(exc_tb.tb_lineno)})