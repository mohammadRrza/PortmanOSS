"""portman_web URL Configuration
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework_nested import routers
from django.conf import settings
import django

from dslam.views import *
from users.views import *

from adminplus.sites import AdminSitePlus
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_swagger.views import get_swagger_view

admin.site = AdminSitePlus()
admin.site.site_title = 'PortMan Admin'
admin.site.site_header = 'Portman Admin Panel'
admin.site.index_title = 'System Administration'
admin.autodiscover()

schema_view = get_swagger_view(title='Pastebin API')

# Router
portman_router = routers.SimpleRouter()
portman_router.register(r'permission', PermissionViewSet, base_name='permission')
portman_router.register(r'profile', PermissionProfileViewSet, base_name='permission-profile')
portman_router.register(r'permission-profile', PermissionProfilePermissionViewSet, base_name='permission-profile-permission')
portman_router.register(r'users/permission-profile', UserPermissionProfileViewSet, base_name='user-permission-profile')
portman_router.register(r'users/auditlog', UserAuditLogViewSet, base_name='user-audit-log')
portman_router.register(r'users', UserViewSet, base_name='users')
portman_router.register(r'mdfdslam', MDFDSLAMViewSet, base_name='mdfdslam')
portman_router.register(r'dslam/bulk-command/result', DSLAMBulkCommandResultViewSet, base_name='dslam-bulk-command-result')
portman_router.register(r'dslam/dslam-type', DSLAMTypeViewSet, base_name='dslam-type')
portman_router.register(r'dslam/cart', DSLAMCartViewSet, base_name='dslam')
portman_router.register(r'dslam/location', DSLAMLocationViewSet, base_name='dslam-location')
portman_router.register(r'dslam/faulty-config', DSLAMFaultyConfigViewSet, base_name='dslam-faulty-config')
portman_router.register(r'dslam/command/result', DSLAMCommandViewSet, base_name='dslam-command')
portman_router.register(r'dslam/events', DSLAMEventViewsSet, base_name='dslam-event')
portman_router.register(r'lineprofile', LineProfileViewSet, base_name='line-profile')
portman_router.register(r'dslam', DSLAMViewSet, base_name='dslam')
portman_router.register(r'dslamport/faulty', DSLAMPortFaultyViewSet, base_name='dslam-port-faulty')
portman_router.register(r'dslamport/events', DSLAMPortEventViewsSet, base_name='dslam-port-event')
portman_router.register(r'dslamport/vlan', DSLAMPortVlanViewSet, base_name='dslam-port-vlan')
portman_router.register(r'telecom-center/mdf', TelecomCenterMDFViewSet, base_name='telecom_center_mdf')
portman_router.register(r'telecom-center/location', TelecomCenterLocationViewSet, base_name='telecom-center-location')
portman_router.register(r'telecom-center', TelecomCenterViewSet, base_name='telecom-center')
portman_router.register(r'dslam-port', DSLAMPortViewSet, base_name='dslam-port')
#portman_router.register(r'dslam-port-snapshot', DSLAMPortSnapshotViewSet, base_name='dslam-port-snapshot')
portman_router.register(r'vlan', VlanViewSet, base_name='vlan')
portman_router.register(r'reseller', ResellerViewSet, base_name='reseller')
portman_router.register(r'customer-port', CustomerPortViewSet, base_name='customer-port')
portman_router.register(r'port-command', PortCommandViewSet, base_name='port-command')
portman_router.register(r'command', CommandViewSet, base_name='command')
portman_router.register(r'city/location', CityLocationViewSet, base_name='city-location')
portman_router.register(r'city', CityViewSet, base_name='city')
portman_router.register(r'reseller-port', ResellerPortViewSet, base_name='reseller-port')
portman_router.register(r'terminal', TerminalViewSet, base_name='terminal')

urlpatterns = [
    url(r'^users/get-token', obtain_jwt_token),
    url(r'^apis-doc/v1/', schema_view),
    #url(r'/', include('rest_framework_swagger.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/dslamport/register-port/$', RegisterPortAPIView.as_view(), name='register-port'),
    url(r'^api/v1/dslamport/run-command/$', RunCommandAPIView.as_view(), name='run-command'),
    url(r'^api/v1/dslamport/port-status-report/$', PortStatusReportView.as_view(), name='port-status-report'),
    url(r'^api/v1/dslamport/port-info/$', GetPortInfoView.as_view(), name='get-port-info'),
    url(r'^api/v1/dslamport/port-admin-status/$', ChangePortAdminStatusView.as_view(), name='change-port-admin-status'),
    url(r'^api/v1/dslamport/reset-admin-status/$', ResetAdminStatusView.as_view(), name='reset-admin-status'),
    url(r'^api/v1/dslamport/port-line-profile/$', ChangePortLineProfileView.as_view(), name='change-port-line-profile'),
    url(r'^api/v1/dslamport/command/$', DSLAMPortRunCommandView.as_view(), name='dslam-port-run-command'),
    url(r'^api/v1/dslam/icmp/command/$', DSLAMRunICMPCommandView.as_view(), name='dslam-run-icmp-command'),
    url(r'^api/v1/dslam/bulk-command/$', BulkCommand.as_view(), name='bulk-command'),
    url(r'^api/v1/quick-search/$', QuickSearchView.as_view(), name='quick-search'),
    url(r'^api/v1/', include(portman_router.urls)),
    url(r'^media/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
]

