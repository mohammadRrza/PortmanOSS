
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from dslam.models import Reseller, DSLAM, DSLAMPort, Command, ResellerPort, MDFDSLAM
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField


class User(AbstractUser):
    USER_TYPES = (
        ('ADMIN', 'Admin'),
        ('SUPPORT', 'Support'),
        ('RESELLER', 'Reseller'),
    )
    type = models.CharField(max_length=20, choices=USER_TYPES, default='ADMIN')
    tel = models.CharField(max_length=15, blank=True, null=True)
    reseller = models.ForeignKey(Reseller, blank=True, null=True)

    ############# permission related properties ##########
    @property
    def denied_telecom_center_ids(self):
        dslam_ids = UserPermissionProfileObject.objects.filter(
            object_id__isnull=False,
            content_type__model='telecom center',
            user_permission_profile__user=self,
            user_permission_profile__action='deny',
            user_permission_profile__is_active=True,
        ).values_list('object_id', flat=True)
        return dslam_ids


    @property
    def allowed_telecom_centers(self):
        if self.type == "RESELLER":
            identifier_keys = ResellerPort.objects.filter(reseller=self.reseller).values_list('identifier_key', flat=True)
            mdf_dslams = MDFDSLAM.objects.filter(identifier_key__in=identifier_keys)
            telecom_centers = mdf_dslams.distinct('telecom_center_id').values_list('telecom_center_id', flat=True)
            return telecom_centers
        else:
            permission = Permission.objects.get(codename='view_telecom_center')
            pp = PermissionProfilePermission.objects.filter(permission=permission)[0]
            upp = self.userpermissionprofile_set.filter(permission_profile=pp.permission_profile)

            user_permission_profile_telecom_center_ids = UserPermissionProfileObject.objects.filter(
                object_id__isnull=False,
                content_type__model='telecom center',
                user_permission_profile__user=self,
                user_permission_profile__action='allow',
                user_permission_profile__is_active=True,
            ).exclude(object_id__in=self.denied_telecom_center_ids).values_list('object_id', flat=True)

            allowed_telecom_centers = {}
            if pp:
                if len(user_permission_profile_telecom_center_ids) > 0:
                    for user_permission_profile_telecom_center_id in user_permission_profile_telecom_center_ids:
                        allowed_telecom_centers[user_permission_profile_telecom_center_id] = pp

                else:
                    for telecom_center_id in TelecomCenter.objects.all().values_list('id', flat=True):
                        if telecom_center_id not in self.denied_telecom_center_ids:
                            allowed_telecom_centers[telecom_center_id] = pp

            return allowed_telecom_centers

    @property
    def denied_dslam_ids(self):
        dslam_ids = UserPermissionProfileObject.objects.filter(
            object_id__isnull=False,
            content_type__model='dslam',
            user_permission_profile__user=self,
            user_permission_profile__action='deny',
            user_permission_profile__is_active=True,
        ).values_list('object_id', flat=True)
        return dslam_ids


    @property
    def allowed_dslams(self):
        if self.type == "RESELLER":
            if self.reseller.name == 'fanava':
                identifier_keys = ResellerPort.objects.filter(reseller=self.reseller).values_list('identifier_key', flat=True)
                mdf_dslams = MDFDSLAM.objects.filter(identifier_key__in=identifier_keys)
                dslams = mdf_dslams.distinct('dslam_id').values_list('dslam_id', flat=True)
            else:
                dslams = ResellerPort.objects.filter(reseller=self.reseller).values_list('dslam_id', flat=True)

            return dslams

        else:
            permission = Permission.objects.get(codename='view_dslam')
            pp = PermissionProfilePermission.objects.filter(permission=permission)[0]
            upp = self.userpermissionprofile_set.filter(permission_profile=pp.permission_profile)

            user_permission_profile_dslam_ids = UserPermissionProfileObject.objects.filter(
                object_id__isnull=False,
                content_type__model='dslam',
                user_permission_profile__user=self,
                user_permission_profile__action='allow',
                user_permission_profile__is_active=True,
            ).exclude(object_id__in=self.denied_dslam_ids).values_list('object_id', flat=True)

            allowed_dslams = {}
            if pp:
                if len(user_permission_profile_dslam_ids) > 0:
                    for user_permission_profile_dslam_id in user_permission_profile_dslam_ids:
                        allowed_dslams[user_permission_profile_dslam_id] = pp

                else:
                    for dslam_id in DSLAM.objects.all().values_list('id', flat=True):
                        if dslam_id not in self.denied_dslam_ids:
                            allowed_dslams[dslam_id] = pp

            return allowed_dslams

    @property
    def denied_dslamport_ids(self):
        dslamport_ids = UserPermissionProfileObject.objects.filter(
            object_id__isnull=False,
            content_type__model='dslamport',
            user_permission_profile__user=self,
            user_permission_profile__action='deny',
            user_permission_profile__is_active=True,
        ).values_list('object_id', flat=True)
        return dslamport_ids

    @property
    def allowed_ports(self):
        allowed_dslam_port = {}
        denied_dslam_port = []
        if self.type == "RESELLER":
            if self.reseller.name == 'fanava':
                identifier_keys = ResellerPort.objects.filter(reseller=self.reseller).values_list('identifier_key', flat=True)
                mdf_dslams = MDFDSLAM.objects.extra(select={'dslam_slot':'slot_number', 'dslam_port':'port_number'}).filter(identifier_key__in=identifier_keys)
                dslamports = mdf_dslams.values('dslam_id', 'dslam_slot', 'dslam_port')
            else:
                dslamports = ResellerPort.objects.filter(reseller=self.reseller).values('dslam_id', 'dslam_slot', 'dslam_port')

            dslam_port_ids = []
            for dslamport in dslamports:
                try:
                    dslam_port_obj = DSLAMPort.objects.get(dslam__id=dslamport['dslam_id'],
                                                       #slot_number=dslamport['slot_number'],
                                                       #port_number=dslamport['port_number'])
                                                       slot_number=dslamport['dslam_slot'],
                                                       port_number=dslamport['dslam_port'])
                    dslam_port_ids.append(dslam_port_obj.pk)
                except Exception as ex:
                    print(dslamport)
                    print(dslamport['dslam_id'], dslamport['dslam_slot'], dslamport['dslam_port'])
                    print(ex)
            return dslam_port_ids
        else:
            for dslam_id, user_pp in self.allowed_dslams.items():
                for dslam_port in DSLAMPort.objects.filter(dslam__id=dslam_id):
                    allowed_dslam_port[dslam_port.pk] = user_pp
        return allowed_dslam_port

    @property
    def denied_commands(self):
        command_ids = UserPermissionProfileObject.objects.filter(
            object_id__isnull=False,
            content_type__model='command',
            user_permission_profile__user=self,
            user_permission_profile__action='deny',
            user_permission_profile__is_active=True,
        ).values_list('object_id', flat=True)
        return command_ids

    @property
    def allowed_commands(self):
        allowed_command = {}
        denied_dslam_port = []
        if self.type == "RESELLER":
            command_permission_ids = UserPermissionProfileObject.objects.filter(
                object_id__isnull=False,
                content_type__model='command',
                user_permission_profile__user=self,
                user_permission_profile__action='allow',
                user_permission_profile__is_active=True,
            ).exclude(object_id__in=self.denied_commands).values_list('object_id', flat=True)
            return command_permission_ids
        else:
            command_permission_objs = UserPermissionProfileObject.objects.filter(
                object_id__isnull=False,
                content_type__model='command',
                user_permission_profile__user=self,
                user_permission_profile__action='allow',
                user_permission_profile__is_active=True,
            )

            if command_permission_objs.count() > 0:
                for command_permission_obj in command_permission_objs:
                    allowed_command[command_permission_obj.object_id] = command_permission_obj
            else:

                permission = Permission.objects.get(codename='view_command')
                pp = PermissionProfilePermission.objects.filter(permission=permission)[0]
                upp = self.userpermissionprofile_set.filter(permission_profile=pp.permission_profile)
                if upp.count() > 0:
                    for command_id in Command.objects.all().values_list('id', flat=True):
                        if command_id not in self.denied_commands:
                            allowed_command[command_id] = pp
        return allowed_command

    ############# permission related methods ##########
    def get_user_telecom_centers(self, permission_name):
        if self.type == "RESELLER":
            return self.allowed_telecom_centers
        else:
            telecom_center_ids = []
            allowed_telecom_centers = self.allowed_telecom_centers
            for telecom_center_id, user_pp in telecom_center_ids.items():
                if user_pp.permission_profile.permissionprofilepermission_set.filter(
                        permission__codename=permission_name
                ).exists():
                    telecom_center_ids.append(telecom_center_id)
            return telecom_center_ids

    def get_user_dslams(self, permission_name):
        if self.type == "RESELLER":
            return self.allowed_dslams
        else:
            dslam_ids = []
            allowed_dslams = self.allowed_dslams
            for dslam_id, user_pp in allowed_dslams.items():
                if user_pp.permission_profile.permissionprofilepermission_set.filter(
                        permission__codename=permission_name
                ).exists():
                    dslam_ids.append(dslam_id)
            return dslam_ids

    def get_user_dslamports(self, permission_name):
        port_ids = []
        allowed_ports = self.allowed_ports
        if self.type == "RESELLER":
            return allowed_ports
        for port_id, user_pp in allowed_ports.items():
            '''
            if user_pp.permission_profile.permissionprofilepermission_set.filter(
                permission__title=permission_name
            ).exists():
            '''
            port_ids.append(port_id)
        return port_ids

    def get_user_commands(self, permission_name):
        return self.allowed_commands

    def has_permission(self, permission_name):
        if self.is_superuser:
            return True
        for user_permission_profile in self.userpermissionprofile_set.filter(is_active=True, action='allow'):
            if user_permission_profile.permission_profile.permissionprofilepermission_set.filter(
                permission__name=permission_name
            ).exists():
                return True
        return False

    def has_permission_to_telecom_center(self, permission_name, telecom_center_id):
        if self.is_superuser:
            return True

        allowed_telecom_centers = self.telecom_centers

        if self.type == 'RESELLER':
            if dslam_id in allowed_telecom_centers:
                return True
            else:
                return False

        if telecom_center_id not in list(allowed_telecom_centers.keys()):
            return False

        if not allowed_telecom_centers[telecom_center_id].permission_profile.permissionprofilepermission_set.filter(
            permission__codename=permission_name
        ).exists():
            return False
        return True


    def has_permission_to_dslam(self, permission_name, dslam_id):
        if self.is_superuser:
            return True

        allowed_dslams = self.allowed_dslams
        if self.type == "RESELLER":
            if dslam_id in allowed_dslams:
                return True
            else:
                return False


        if dslam_id not in list(allowed_dslams.keys()):
            return False

        if not allowed_dslams[dslam_id].permission_profile.permissionprofilepermission_set.filter(
            permission__codename=permission_name
        ).exists():
            return False
        return True

    def has_permission_to_dslamport(self, permission_name, port_id):
        if self.is_superuser:
            return True

        allowed_ports = self.allowed_ports


        if self.type == "RESELLER":
            if port_id in allowed_ports:
                return True
            else:
                return False

        if port_id not in list(allowed_ports.keys()):
            return False


        if not allowed_ports[port_id].permission_profile.permissionprofilepermission_set.filter(
            permission__codename=permission_name
        ).exists():
            return False
        return True


class UserAuditLog(models.Model):
    username = models.CharField(max_length=256)
    model_name = models.CharField(max_length=100)
    instance_id = models.IntegerField(blank=True, null=True)
    action = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    ip = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{0}({1})'.format(self.username, self.action)

    class Meta:
        ordering = ('-created_at',)


class Permission(models.Model):
    title = models.CharField(max_length=256)
    codename = models.CharField(max_length=256, verbose_name='code name', unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'permission'
        verbose_name_plural = 'permissions'

    def __unicode__(self):
        return self.title


class PermissionProfile(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name


class PermissionProfilePermission(models.Model):
    permission_profile = models.ForeignKey(PermissionProfile)
    permission = models.ForeignKey(Permission)

    class Meta:
        unique_together = (('permission_profile', 'permission'),)

    def __unicode__(self):
        return '{0}({1})'.format(self.permission_profile.name, self.permission.title)


class UserPermissionProfile(models.Model):
    ACTIONS = (
        ('allow', 'Allow'),
        ('deny', 'Deny'),
    )
    user = models.ForeignKey(User)
    permission_profile = models.ForeignKey(PermissionProfile, blank=True, null=True)
    action = models.CharField(choices=ACTIONS, max_length=30, default='allow')
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.user.username


class UserPermissionProfileObject(models.Model):
    user_permission_profile = models.ForeignKey(UserPermissionProfile)
    content_type = models.ForeignKey(
            ContentType,
            models.CASCADE,
            verbose_name='content type',
            related_name='user_permission_content_type', blank=True, null=True)
    object_id = models.IntegerField(blank=True, null=True)

    def as_json(self):
        name = None
        model_type = self.content_type.model
        if model_type == 'dslam':
            name = DSLAM.objects.get(id=self.object_id).name
        elif model_type == 'command':
            name = Command.objects.get(id=self.object_id).text
        return {
                'id': self.id,
                'user_permission_profile_id': self.user_permission_profile.id,
                'model_type': self.content_type.model,
                'object_id': self.object_id,
                'object_name': name
            }

    class Meta:
        unique_together = (('user_permission_profile', 'content_type', 'object_id'),)
