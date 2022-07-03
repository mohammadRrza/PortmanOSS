from django.contrib.auth import get_user_model

from rest_framework import serializers
from dslam.serializers import ResellerSerializer

from users.models import *

from khayyam import JalaliDatetime


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    last_login = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)
    date_joined = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    reseller_info = ResellerSerializer(source='reseller', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'tel',
            'last_name', 'last_login', 'is_active', 'type',
            'date_joined', 'confirm_password', 'password',
            'reseller_info', 'reseller',
        )

        read_only_fields = ('id', 'date_joined', 'last_login', 'is_active')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Password mismatch")
        del data['confirm_password']
        return data

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'tel', 'reseller',
        )

    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError('Email already exists')
        return value


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'password', 'new_password', 'confirm_password'
        )

    def validate_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError("Invalid password")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Password mismatch")
        return data


class UserAuditLogSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_persian_date')

    def get_created_persian_date(self, obj):
        return JalaliDatetime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = UserAuditLog
        fields = ('username', 'model_name', 'instance_id', 'action', 'description', 'ip', 'created_at')


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'title', 'codename', 'description')


class PermissionProfileSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField(read_only=True, required=False)

    def get_permissions(self, obj):
        permissions = obj.permissionprofilepermission_set.all()
        return [{'id': p.permission.pk, 'name': p.permission.title} for p in permissions]

    class Meta:
        model = PermissionProfile
        fields = ('id', 'name', 'permissions')


class PermissionProfilePermissionSerializer(serializers.ModelSerializer):
    permission_info = PermissionSerializer(source='permission', read_only=True, required=False)
    permission_profile_info = PermissionProfileSerializer(source='permission_profile', read_only=True, required=False)

    class Meta:
        model = PermissionProfilePermission
        fields = ('id', 'permission_profile', 'permission', 'permission_profile_info', 'permission_info')


class UserPermissionProfileSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True, required=False)
    permission_profile_name = serializers.CharField(source='permission_profile.name', read_only=True)

    class Meta:
        model = UserPermissionProfile
        fields = ('id', 'user', 'user_info', 'action', 'is_active', 'permission_profile', 'permission_profile_name')


class PortmanLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortmanLog
        fields = '__all__'
