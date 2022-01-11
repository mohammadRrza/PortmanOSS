
"""portman_web URL Configuration
"""
from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from rest_framework_nested import routers
from django.conf import settings
import django

from dslam.views import *
from users.views import *
from router.views import *
from switch.views import *
from contact.views import *
from radio.views import *

from modem.views import GetModemInfoAPIView
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
portman_router.register(r'users', UserViewSet, basename='users')
portman_router.register(r'users-permission-profile', UserPermissionProfileViewSet, basename='user-permission-profile')
portman_router.register(r'users', UserViewSet, basename='users')
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
portman_router.register(r'router', RouterViewSet, basename='router')
portman_router.register(r'switch', SwitchViewSet, basename='switch')
portman_router.register(r'switch-command', SwitchCommandViewSet, basename='switch_command')
portman_router.register(r'router-command', RouterCommandViewSet, basename='router_command')
portman_router.register(r'contact/portmap', PortMapViewSet, basename='contact')
portman_router.register(r'radio', RadioViewSet, basename='radio')
portman_router.register(r'radio-command', RadioCommandViewSet, basename='radio-command')
portman_router.register(r'portman-log', PortmanLogViewSet, basename='portman-log')

urlpatterns = [
    url(r'^users/get-token', obtain_jwt_token),
    url(r'^apis-doc/v1/', schema_view),
    url(r'/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/dslamport/register-port/$', RegisterPortAPIView.as_view(), name='register-port'),
    #url(r'^api/v1/dslamport/run-command/$', RunCommandAPIView.as_view(), name='run-command'),
    url(r'^api/v1/dslamport/port-status-report/$', PortStatusReportView.as_view(), name='port-status-report'),
    url(r'^api/v1/dslamport/port-info/$', GetPortInfoView.as_view(), name='get-port-info'),
    url(r'^api/v1/dslamport/port-admin-status/$', ChangePortAdminStatusView.as_view(), name='change-port-admin-status'),
    url(r'^api/v1/dslamport/reset-admin-status/$', ResetAdminStatusView.as_view(), name='reset-admin-status'),
    url(r'^api/v1/dslamport/port-line-profile/$', ChangePortLineProfileView.as_view(), name='change-port-line-profile'),
    url(r'^api/v1/dslamport/UpdateBukht/$', BukhtUpdateAPIView.as_view(), name='Bukht-Update'),
    url(r'^api/v1/dslamport/getFreePortInfo/$', GetFreePortInfoAPIView.as_view(), name='Get-Free-Port-Info'),
    url(r'^api/v1/dslamport/command/$', DSLAMPortRunCommandView.as_view(), name='dslam-port-run-command'),
    url(r'^api/v1/dslamport/command2/$', DSLAMPortRunCommand2View.as_view(), name='dslam-port-run-command'),
    url(r'^api/v1/dslamport/free-Port/$', FreePortAPIView.as_view(), name='freePort'),
    url(r'^api/v1/dslamport/reserve-Port/$', ReservePortAPIView.as_view(), name='reservePort'),
    url(r'^api/v1/dslamport/Add-Customer/$', AddCustomerAPIView.as_view(), name='addCustomer'),
    url(r'^api/v1/dslamport/port-Assign/$', PortAssignAPIView.as_view(), name='portAssign'),
    url(r'^api/v1/dslamport/getBukhtInfo/$', GetBukhtInfoAPIView.as_view(), name='getBukhtInfo'),
    url(r'^api/v1/dslamport/getProvinces/$', GetProvincesAPIView.as_view(), name='getProvinces'),
    url(r'^api/v1/dslamport/getCities/$', GetCitiesAPIView.as_view(), name='getCities'),
    url(r'^api/v1/dslamport/getTelecomCenters/$', GetTelecomCentersAPIView.as_view(), name='getTelecomCenters'),
    url(r'^api/v1/dslamport/getDslams/$', GetDslamsAPIView.as_view(), name='getDslams'),
    url(r'^api/v1/dslamport/getUserPortInfo/$', GetUserPortInfoAPIView.as_view(), name='getUserPortInfo'),
    url(r'^api/v1/dslamport/getCommandInfoSnmp/$', GetCommandInfoSnmp.as_view(), name='getCommandInfoSnmp'),
    url(r'^api/v1/dslamport/getCommandInfoTelnet/$', GetCommandInfoTelnet.as_view(), name='getCommandInfoTelnet'),
    url(r'^api/v1/dslamport/getPortInfoByUsername/$', GetPortInfoByUserNameAPIView.as_view(), name='getPortInfoByUsername'),
    url(r'^api/v1/dslamport/registerPortByResellerId/$', RegisterPortByResellerIdAPIView.as_view(), name='registerPortByResellerId'),
    url(r'^api/v1/dslamport/getAllFreePorts/$', GetAllFreePortsAPIView.as_view(), name='getAllFreePortsAPI'),
    url(r'^api/v1/dslamport/changeBukht/$', ChangeBukhtAPIView.as_view(), name='changeBukht'),
    url(r'^api/v1/dslamport/getPortHistory/$', GetPortHistoryAPIView.as_view(), name='getPortHistory'),
    url(r'^api/v1/dslamport/getDslamBackup/$', GetDslamBackupAPIView.as_view(), name='getDslamBackup'),
    url(r'^api/v1/dslamport/SendMail/$', SendMailAPIView.as_view(), name='SendMail'),
    url(r'^api/v1/dslamport/getPortInfoById/$', GetPortInfoByIdAPIView.as_view(), name='getPortInfoById'),
    #url(r'^api/v1/dslamport/fiberHomeCommand/$', FiberHomeCommandAPIView.as_view(), name='fiberHomeComman'),
    url(r'^api/v1/dslamport/run-command/$', FiberHomeCommandAPIView.as_view(), name='fiberHomeComman'),
    url(r'^api/v1/dslamport/dslam_commandsV2/$', DslamCommandsV2APIView.as_view(), name='fiberHomeComman'),
    url(r'^api/v1/dslamport/runCommandByIP/$', RunCommandByIPAPIView.as_view(), name='runCommandByIP'),
    url(r'^api/v1/dslamport/bitstreamFreePort/$', BitstreamFreePortAPIView.as_view(), name='bitstreamFreePort'),
    url(r'^api/v1/dslamport/getDslamBackupByIdAPIView/$', GetDslamBackupByIdAPIView.as_view(), name='getDslamBackupByIdAPIView'),
    url(r'^api/v1/dslamport/updateProfile/$', UpdateProfileAPIView.as_view(), name='updateProfile'),
    url(r'^api/v1/dslamport/setTimeAllDslams/$', SetTimeAllDslamsAPIView.as_view(), name='setTimeAPIView'),
    url(r'^api/v1/dslamport/getPortDownstream/$', GetPortDownstreamAPIView.as_view(), name='getPortDownstreamAPIView'),
    url(r'^api/v1/dslamport/saveLineStats/$', SaveLineStatsAPIView.as_view(), name='saveLineStats'),
    url(r'^api/v1/dslamport/getSeltByFqdn/$', GetSeltByFqdnAPIView.as_view(), name='getSeltByFqdn'),
    # url(r'^api/v1/dslamport/createTicket/$', CreateTicketAPIView.as_view(), name='createTicket'),
    # url(r'^api/v1/dslamport/getticket/$', GetTicketInfoAPIView.as_view(), name='getticket'),
    url(r'^api/v1/dslamport/port_conflict_correction/$', PortConflictCorrectionAPIView.as_view(), name='port_conflict_correction'),
    url(r'^api/v1/dslamport/addTicket/$', AddTicketDanaAPIView.as_view(), name='addTicket'),
    url(r'^api/v1/dslamport/get_ticket_Details/$', GetTicketDetailsDanaAPIView.as_view(), name='get_ticket_Details'),
    url(r'^api/v1/dslamport/get_hosts_from_zabbix/$', GetHostsFromZabbixAPIView.as_view(), name='get_hosts_from_zabbix'),
    url(r'^api/v1/dslamport/check_network_bulk_availability/$', CheckNetworkBulkAvailability.as_view(), name='check_network_bulk_availability'),
    url(r'^api/v1/dslamport/get_hosts_from_zabbix/$', GetHostsFromZabbixAPIView.as_view(), name='get_hosts_from_zabbix'),
    url(r'^api/v1/dslam/get_items_from_zabbix/$', GetItemsFromZabbixAPIView.as_view(), name='get_items_from_zabbix'),
    url(r'^api/v1/dslam/bulk-command/$', BulkCommand.as_view(), name='bulk-command'),
    url(r'^api/v1/dslam/ngn_register/$', NGNRegisterAPIView.as_view(), name='bulk-command'),

    url(r'^api/v1/dslam/get_dslams_packet_loss_count/$', DslamIcmpSnapshotCount.as_view(), name='get_dslams_packet_loss_count'),
    url(r'^api/v1/dslam/get_interface_traffic_input/$', GetInterfaceTrafficInput.as_view(), name='get_interface_traffic_input'),
    url(r'^api/v1/dslam/zabbix_get_history/$', ZabbixGetHistory.as_view(), name='zabbix_get_history'),
    url(r'^api/v1/dslam/get_fifty_five_precntage/$', GetFiftyFivePercent.as_view(), name='get_finety_five_precntage'),
    url(r'^api/v1/dslam/get_fifty_five_precntage/$', GetFiftyFivePercent.as_view(), name='get_fifty_five_precntage'),
    url(r'^api/v1/quick-search/$', QuickSearchView.as_view(), name='quick-search'),

    url(r'^api/v1/dslamport/ranjeNumber-Inquiry/$', RanjeNumberInquiryAPIView.as_view(), name='ranjeNumberInquiry'),
    url(r'^api/v1/dslamport/fetch-shaskam-inquiry/$', FetchShaskamInquiryAPIView.as_view(), name='fetchShaskamInquiry'),
    url(r'^api/v1/dslamport/set-shaskam-inquiry/$', SetShaskamInquiryAPIView.as_view(), name='setShaskamInquiry'),
    url(r'^api/v1/dslam/icmp/command/$', DSLAMRunICMPCommandView.as_view(), name='dslam-run-icmp-command'),
    url(r'^api/v1/dslam/icmp_by_fqdn/command/$', DSLAMRunICMPCommandByFqdnView.as_view(), name='icmp_by_fqdn'),
    url(r'^api/v1/dslamport/check_port_conflict/$', CheckPortConflict.as_view(),
        name='check_port_conflict'),
    url(r'^api/v1/dslam/load_dslam_ports/$', LoadDslamPorts.as_view(), name='load_dslam_ports'),
    url(r'^api/v1/dslamport/get_port_count/$', GetDslamPorts.as_view(), name='get_port_count'),
    url(r'^api/v1/dslamport/fiberhome_get_card/$', FiberHomeGetCardAPIView.as_view(), name='fiberhome_get_card'),
    url(r'^api/v1/dslamport/fiberhome_get_port/$', FiberHomeGetPortAPIView.as_view(), name='fiberhome_get_port'),
    url(r'^api/v1/dslamport/upload_rented_port/$', UploadRentedPort.as_view(), name='upload_rented_port'),
    url(r'^api/v1/dslamport/rented_port/$', RentedPortAPIView.as_view(), name='rented_port'),
    url(r'^api/v1/dslamport/get_pvc_vlan/$', GetPVCVlanAPIView.as_view(), name='get_pvc_vlan'),
    url(r'^api/v1/dslamport/add_to_vlan/$', AddToVlanAPIView.as_view(), name='add_to_vlan'),
    url(r'^api/v1/dslamport/portmap/$', PortmapAPIView.as_view(), name='portmap'),
    url(r'^api/v1/dslamport/get-captcha/$', GetCaptchaAPIView.as_view(), name='get-captcha'),
    url(r'^api/v1/dslamport/farzanegan_scrapping/$', FarzaneganScrappingAPIView.as_view(), name='farzanegan_scrapping'),

    # Routers
    # url(r'^api/v1/dslam/icmp_by_fqdn/connect_handler_test/$', ConnectHandlerTest.as_view(),name='connect_handler_test'),
    url(r'^api/v1/router-command/router_run_command/$', RouterRunCommandAPIView.as_view(), name='routerRunCommand'),
    url(r'^api/v1/router/router_run_command/$', RouterRunCommandAPIView.as_view(), name='routerRunCommand'),
    url(r'^api/v1/router/get_router_backup_files_name/$', GetRouterBackupFilesNameAPIView.as_view(),
        name='get_backup_files_name'),
    url(r'^api/v1/router/get_router_backup_files_name2/$', GetRouterBackupFilesNameAPIView2.as_view(),
        name='get_backup_files_name'),
    url(r'^api/v1/router/download_router_backup_file/$', DownloadRouterBackupFileAPIView.as_view(), name='download_router_backup_file'),
    url(r'^api/v1/router/get_router_backup_error_file/$', GetRouterBackupErrorFilesNameAPIView.as_view(),
        name='get_router_backup_error_file'),
    url(r'^api/v1/router-command/read_router_backup_error_files_name/$', ReadRouterBackupErrorFilesNameAPIView.as_view(),
        name='read_router_backup_error_files_name'),
    url(r'^api/v1/router/set_ssl_on_router/$', SetSSLOnRouter.as_view(),
        name='set_ssl_on_router'),

    # Switches
    url(r'^api/v1/switch/switch_run_command/$', SwitchRunCommandAPIView.as_view(), name='switch_run_command'),
    url(r'^api/v1/switch/get_switch_backup_files_name/$', GetSwitchBackupFilesNameAPIView.as_view(), name='get_switch_backup_files_name'),
    url(r'^api/v1/switch/download_backup_file/$', DownloadBackupFileAPIView.as_view(), name='download_backup_file'),
    url(r'^api/v1/switch/get_backup_error_file/$', GetBackupErrorFilesNameAPIView.as_view(),
        name='get_backup_error_file'),
    url(r'^api/v1/switch/get_backup_error_text/$', GetBackupErrorTextNameAPIView.as_view(),
        name='get_backup_error_file'),
    url(r'^api/v1/switch/read_switch_backup_error_files_name/$', ReadSwitchBackupErrorFilesNameAPIView.as_view(),
        name='read_switch_backup_error_files_name'),
    url(r'^api/v1/switch/get_switch_show_vlan_brief_files_name/$', GetSwitchShowVlanBriefFilesName.as_view(),
        name='get_switch_show_vlan_brief_files_name'),
    url(r'^api/v1/switch/download_view_vlan_brief_file/$', DownloadViewVlanBriefFile.as_view(),
        name='download_view_vlan_brief_file'),

    # Radio
    url(r'^api/v1/radio/get_radio_backup_files_name/$', GetRadioBackupFilesNameAPIView.as_view(),
        name='get_radio_backup_files_name'),

    url(r'^api/v1/radio/download_radio_backup_file/$', DownloadRadioBackupFileAPIView.as_view(),
        name='download_radio_backup_file'),
    url(r'^api/v1/radio/read_radio_backup_error_files_name/$', ReadRadioBackupErrorFilesNameAPIView.as_view(),
        name='download_radio_backup_file'),
    url(r'^api/v1/radio/set_radio_geographical_coordinates/$', SetRadioGeographicalCoordinatesAPIView.as_view(),
        name='set_radio_geographical_coordinates'),

    url(r'^api/v1/contact/get_provinces/$', GetProvincesAPIView.as_view(),
        name='get_provinces'),
    url(r'^api/v1/contact/get_cities_by_province_id/$', GetCitiesByProvinceIdAPIView.as_view(),
        name='get_cities'),
    url(r'^api/v1/contact/get_telecoms_by_city_id/$', GetTelecomsByCityIdAPIView.as_view(),
        name='get_telecoms_by_city_id'),
    url(r'^api/v1/contact/get_port_statuses/$', GetPortsStatus.as_view(),
        name='get_port_statuses'),
    url(r'^api/v1/contact/search_ports/$', SearchPorts.as_view(),
        name='search_ports'),
    url(r'^api/v1/contact/update_status_ports/$', UpdateStatusPorts2.as_view(),
        name='update_status_ports'),
    url(r'^api/v1/contact/get_cities_from_pratak/$', GetCitiesFromPratakAPIView.as_view(),
        name='get_cities_from_pratak'),

#portman_cdms
    url(r'^api/v1/portman_cdms/get_user_port_info/$', GetUserPortInfoFromPartakAPIView.as_view(), name='get_user_port_info'),
    url(r'^api/v1/portman_cdms/get_dslam_id_by_fqdn/$', GetDslamIdByFqdnAPIView.as_view(), name='get_dslam_id_by_fqdn'),
    url(r'^api/v1/portman_cdms/get_fqdn_from_zabbix_by_ip/$', GetFqdnFromZabbixByIpAPIView.as_view(), name='get_fqdn_from_zabbix_by_ip'),
    url(r'^api/v1/portman_cdms/get_dslam_id_by_ip/$', GetDSLAMIdByIPAPIView.as_view(),
        name='get_fqdn_from_zabbix_by_ip'),
    url(r'^api/v1/portman_cdms/get_fqdn_from_zabbix/$', GetFqdnFromZabbixAPIView.as_view(),
        name='get_fqdn_from_zabbix_by_ip'),

    url(r'^api/v1/', include(portman_router.urls)),

    url(r'^media/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),

]

