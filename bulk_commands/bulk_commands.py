from Commands.get_backups import GetbackUp
from Commands.get_mikrotik_routers_backup import GetMikrotikbackUp
from Commands.get_vlan_brief import GetVlanBrief
from Commands.get_cisco_switches_backup import GetCiscoSwitchbackUp
from Commands.get_zabbix_hosts import ZabbixHosts
from Commands.get_mikrotik_radio_backup import GetMikrotikRadiobackUp
from Commands.get_cisco_routers_backup import GetCiscoRouterbackUp
from Commands.ip_service_set import SetIPService
from Commands.get_dslam_port_params import GetDslamPortParams

if __name__ == '__main__':
    '''back_up = GetbackUp()
    print('Backup process is started.')
    back_up.run_command()
    ip_service_set = SetIPService()
    ip_service_set.run_command()'''

    zabbix_hosts = ZabbixHosts()
    zabbix_hosts.get_zabbix_hosts()
    cisco_switches_backup = GetCiscoSwitchbackUp()
    GetCiscoSwitchbackUp.run_command(self=None)
    mikrotik_routers_backup = GetMikrotikbackUp()
    mikrotik_routers_backup.run_command()
    get_vlan_brief = GetVlanBrief()
    get_vlan_brief.run_command()
    cisco_routers_backup = GetCiscoRouterbackUp()
    cisco_routers_backup.run_command()
    # #radio_backup = GetMikrotikRadiobackUp()
    # #radio_backup.run_command()

