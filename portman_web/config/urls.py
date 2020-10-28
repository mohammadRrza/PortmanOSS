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
portman_router.register(r'permission', PermissionViewSet, basename='permission')
portman_router.register(r'profile', PermissionProfileViewSet, basename='permission-profile')
portman_router.register(r'permission-profile', PermissionProfilePermissionViewSet, basename='permission-profile-permission')
portman_router.register(r'users/permission-profile', UserPermissionProfileViewSet, basename='user-permission-profile')
portman_router.register(r'users/auditlog', UserAuditLogViewSet, basename='user-audit-log')
portman_router.register(r'mdfdslam', MDFDSLAMViewSet, basename='mdfdslam')
portman_router.register(r'dslam/bulk-command/result', DSLAMBulkCommandResultViewSet, basename='dslam-bulk-command-result')
portman_router.register(r'dslam/dslam-type', DSLAMTypeViewSet, basename='dslam-type')
portman_router.register(r'dslam/cart', DSLAMCartViewSet, basename='dslam')
portman_router.register(r'dslam/location', DSLAMLocationViewSet, basename='dslam-location')
portman_router.register(r'dslam/faulty-config', DSLAMFaultyConfigViewSet, basename='dslam-faulty-config')
portman_router.register(r'dslam/command/result', DSLAMCommandViewSet, basename='dslam-command')
portman_router.register(r'dslam/events', DSLAMEventViewsSet, basename='dslam-event')
portman_router.register(r'lineprofile', LineProfileViewSet, basename='line-profile')
portman_router.register(r'dslam', DSLAMViewSet, basename='dslam')
portman_router.register(r'dslamport/faulty', DSLAMPortFaultyViewSet, basename='dslam-port-faulty')
portman_router.register(r'dslamport/events', DSLAMPortEventViewsSet, basename='dslam-port-event')
portman_router.register(r'dslamport/vlan', DSLAMPortVlanViewSet, basename='dslam-port-vlan')
portman_router.register(r'telecom-center/mdf', TelecomCenterMDFViewSet, basename='telecom_center_mdf')
portman_router.register(r'telecom-center/location', TelecomCenterLocationViewSet, basename='telecom-center-location')
portman_router.register(r'telecom-center', TelecomCenterViewSet, basename='telecom-center')
portman_router.register(r'dslam-port', DSLAMPortViewSet, basename='dslam-port')
#portman_router.register(r'dslam-port-snapshot', DSLAMPortSnapshotViewSet, basename='dslam-port-snapshot')
portman_router.register(r'vlan', VlanViewSet, basename='vlan')
portman_router.register(r'reseller', ResellerViewSet, basename='reseller')
portman_router.register(r'customer-port', CustomerPortViewSet, basename='customer-port')
portman_router.register(r'port-command', PortCommandViewSet, basename='port-command')
portman_router.register(r'command', CommandViewSet, basename='command')
portman_router.register(r'city/location', CityLocationViewSet, basename='city-location')
portman_router.register(r'city', CityViewSet, basename='city')
portman_router.register(r'reseller-port', ResellerPortViewSet, basename='reseller-port')
portman_router.register(r'terminal', TerminalViewSet, basename='terminal')

urlpatterns = [
    url(r'^users/get-token', obtain_jwt_token),
    url(r'^apis-doc/v1/', schema_view),
    #url(r'/', include('rest_framework_swagger.urls')),
    url(r'^admin/', admin.site.urls),
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

