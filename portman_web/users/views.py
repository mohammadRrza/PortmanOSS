import os
import sys

from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model

from rest_framework import viewsets, status, views, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from django.conf import settings

from users.serializers import *
from users.models import UserAuditLog
from dslam.mail import Mail

from django.http import JsonResponse, HttpResponse
import simplejson as json
from khayyam import *
from datetime import date, datetime

from dslam.views import LargeResultsSetPagination

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    Get users
    ---
    parameters:
        - username:
            type: string
            paramType: form
            required: true
        - sort_field:
            type: string
            paramType: form
            required: true
    """
    model = User
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-id')
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        queryset = self.queryset
        username = self.request.query_params.get('username', None)
        first_name = self.request.query_params.get('first_name', None)
        last_name = self.request.query_params.get('last_name', None)
        user_type = self.request.query_params.get('type', None)
        sort_field = self.request.query_params.get('sort_field', None)
        if username:
            queryset = queryset.filter(username__icontains=username)

        if first_name:
            queryset = queryset.filter(first_name__istartswith=first_name)

        if last_name:
            queryset = queryset.filter(last_name__istartswith=last_name)

        if user_type:
            queryset = queryset.filter(type=user_type)

        if sort_field:
            queryset = queryset.order_by(sort_field)

        return queryset

    def create(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            new_user = serializer.save()
            # add_audit_log(
            #    request,
            #    'user',
            #    'create',
            #    object_id=new_user.pk,
            #    description='create user %s'%new_user.username,
            # )
            # save limit ips if exists
            new_user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        """
         Update user
        """

        user = self.get_object()
        data = request.data

        serializer = UserUpdateSerializer(instance=user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True)
    def changepassword(self, request, pk=None):
        """
        Change Password
        ---
        parameters:
            - new_password:
                type: string
                paramType: form
                required: true
        """
        user = self.get_object()
        data = request.data

        serializer = ChangePasswordSerializer(instance=user, data=data)
        if serializer.is_valid():
            user.set_password(data['new_password'])
            user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False, permission_classes=[], authentication_classes=[])
    def login(self, request):
        """
        Login User
        ---
        parameters:
            - username:
                type: string
                paramType: form
                required: true
            - password:
                type: string
                paramType: form
                required: true
        """

        try:
            data = request.data
            username = data.get('username', '')
            password = data.get('password', '')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)

                    # create token
                    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                    payload = jwt_payload_handler(user)
                    token = jwt_encode_handler(payload)

                    response = serializer = UserSerializer(user).data
                    response['token'] = token

                    return Response(response, status=status.HTTP_200_OK)
                else:
                    return Response({'msg': 'User is inactive'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'msg': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return JsonResponse({'result': 'Error is {0}'.format(ex), 'Line': str(exc_tb.tb_lineno)})

    @action(methods=['POST'], detail=False, permission_classes=[], authentication_classes=[])
    def SendResetPasswordLink(self, request):
        try:
            user_mail = request.data.get('email')
            mail_info = Mail()
            mail_info.from_addr = 'oss-problems@pishgaman.net'
            mail_info.to_addr = user_mail
            mail_info.msg_body = 'eeeeeeeeeeeessssssssssssss'
            mail_info.msg_subject = 'Reset Your OSS Passwd'
            Mail.Send_Mail(mail_info)
            return JsonResponse(
                {'row': "ddddd"})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return Response({'message': str(ex) + "  // " + str(exc_tb.tb_lineno)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=False)
    def get_permission(self, request):
        user = request.user
        data = request.data
        pp_list = UserPermissionProfile.objects.filter(user__username=user.username).values_list('permission_profile',
                                                                                                 flat=True)
        permissions = PermissionProfilePermission.objects.filter(permission_profile__in=pp_list).values_list(
            'permission__codename', flat=True)
        return Response({'permissions': permissions, 'user_type': user.type}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        """
        Logout User
        """
        refresh_jwt_token(request)
        logout(request)
        return Response({}, status=status.HTTP_200_OK)


class UserAuditLogViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = UserAuditLogSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = UserAuditLog.objects.all()
        data = self.request.query_params
        keywords = data.get('search_keywords')
        action = data.get('search_action')
        ip = data.get('search_ip')
        username = data.get('search_username')
        start_date = data.get('search_date_from')
        end_date = data.get('search_date_to')
        sort_field = data.get('sort_field')

        if keywords:
            keyword_params = keywords.split(',')
            for keyword in keyword_params:
                print(keyword)
                queryset = queryset.filter(description__icontains=keyword)

        if ip:
            queryset = queryset.filter(ip=ip)

        if action:
            queryset = queryset.filter(action=action)

        if username:
            queryset = queryset.filter(username=username)

        if start_date:
            # for example start_date = 20120505 and end_date = 20120606
            year, month, day = start_date.split('/')
            start_date = JalaliDate(year, month, day).todate()
            if end_date:
                year, month, day = end_date.split('/')
                end_date = JalaliDate(year, month, day).todate()
            else:
                end_date = date.today()

            queryset = queryset.filter(created_at__gte=start_date, created_at__lt=end_date).order_by('created_at')

        if sort_field:
            queryset = queryset.order_by(sort_field)

        return queryset

    @action(methods=['GET'], detail=False)
    def actions(self, request):
        data = tuple(enumerate(UserAuditLog.objects.values_list('action').order_by().distinct(), 1))
        data_dict = [{'id': key, 'text': value} for key, value in data]
        return HttpResponse(json.dumps(data_dict), content_type='application/json; charset=UTF-8')


class PermissionViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = PermissionSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Permission.objects.all()
        title = self.request.query_params.get('search_title', None)
        if title:
            queryset = queryset.filter(title__istartswith=title)

        return queryset

    @action(methods=['GET'], detail=False)
    def get_user_permissions(self, request):
        user = request.user
        data = request.query_params
        username = data.get('username')
        permissions = []
        if username:
            pp_list = UserPermissionProfile.objects.filter(user__username=username).values_list('permission_profile',
                                                                                                flat=True)
            permissions = PermissionProfilePermission.objects.filter(permission_profile__in=pp_list).values_list(
                'permission__codename', flat=True)
        return Response({'results': permissions})


class PermissionProfileViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    serializer_class = PermissionProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = PermissionProfile.objects.all()
        name = self.request.query_params.get('search_name', None)
        if name:
            queryset = queryset.filter(name__istartswith=name)

        return queryset


class PermissionProfilePermissionViewSet(mixins.ListModelMixin,
                                         mixins.CreateModelMixin,
                                         mixins.RetrieveModelMixin,
                                         mixins.UpdateModelMixin,
                                         mixins.DestroyModelMixin,
                                         viewsets.GenericViewSet):
    serializer_class = PermissionProfilePermissionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = PermissionProfilePermission.objects.all()
        return queryset

    @action(methods=['POST'], detail=False)
    def delete_permission_profile(self, request):
        user = request.user
        data = request.data
        permission_profile_id = data.get('permission_profile_id')
        perofile_profile = PermissionProfile.objects.get(id=permission_profile_id)
        PermissionProfilePermission.objects.filter(permission_profile=perofile_profile).delete()
        perofile_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        data = request.data

        permission_profile_obj, permission_profile_created = PermissionProfile.objects.get_or_create(
            name=data.get('permission_profile_name'))
        if not permission_profile_created:
            return Response({'result': 'Permission Profile Name is exist !!!.'}, status=status.HTTP_400_BAD_REQUEST)

        permissions_obj = Permission.objects.filter(id__in=data.get('permissions'))

        for permission_obj in permissions_obj:
            ppp = PermissionProfilePermission()
            ppp.permission_profile = permission_profile_obj
            ppp.permission = permission_obj
            ppp.save()

            # description = u'Create Permission Profile Name: {0}'.format(permission_profile_obj.name)
            # add_audit_log(request, 'PermissionProfile', permission_profile_obj.id, 'Create Permission Profile', description)

        return Response('Permissions Profile created', status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        data = request.data
        permission_profile_obj = PermissionProfile.objects.get(id=data.get('permission_profile_id'))
        permissions = data.get('permissions')
        PermissionProfilePermission.objects.filter(permission_profile=permission_profile_obj).delete()
        permissions_obj = Permission.objects.filter(id__in=permissions)

        for permission_obj in permissions_obj:
            ppp = PermissionProfilePermission()
            ppp.permission_profile = permission_profile_obj
            ppp.permission = permission_obj
            ppp.save()

        return Response('Permissions Profile updated', status=status.HTTP_204_NO_CONTENT)


class UserPermissionProfileViewSet(mixins.ListModelMixin,
                                   mixins.CreateModelMixin,
                                   mixins.RetrieveModelMixin,
                                   mixins.UpdateModelMixin,
                                   mixins.DestroyModelMixin,
                                   viewsets.GenericViewSet):
    serializer_class = UserPermissionProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = UserPermissionProfile.objects.all()
        return queryset

    def create(self, request, *args, **kwargs):
        self.user = request.user
        data = request.data
        objects = data.get('objects')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        upp = UserPermissionProfile.objects.get(id=serializer.data.get('id'))
        if objects:
            for obj in objects:
                for obj_id in obj.get('id', []):
                    user_ppo = UserPermissionProfileObject()
                    user_ppo.user_permission_profile = upp
                    user_ppo.content_type = ContentType.objects.get(model=obj.get('type'))
                    user_ppo.object_id = obj_id
                    user_ppo.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        data = request.data
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        UserPermissionProfileObject.objects.filter(user_permission_profile=instance).delete()
        objects = data.get('objects')
        if objects:
            for obj in objects:
                for obj_id in obj.get('id', []):
                    user_ppo = UserPermissionProfileObject()
                    user_ppo.user_permission_profile = instance
                    user_ppo.content_type = ContentType.objects.get(model=obj.get('type'))
                    user_ppo.object_id = obj_id
                    user_ppo.save()

        return Response('Permissions Profile User Updated', status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=True)
    def objects(self, request, pk=None):
        user = request.user
        data = self.request.query_params
        upp_id = self.get_object().id
        uppo_list = [item.as_json() for item in
                     UserPermissionProfileObject.objects.filter(user_permission_profile__id=upp_id)]
        return JsonResponse({'result': uppo_list})

    """
    Destroy a model instance.
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        UserPermissionProfileObject.objects.filter(user_permission_profile=instance).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
