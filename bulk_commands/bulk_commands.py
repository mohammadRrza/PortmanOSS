from Commands.get_backups import GetbackUp
from Commands.get_mikrotik_routers_backup import GetMikrotikbackUp
from Commands.get_vlan_brief import GetVlanBrief

if __name__ == '__main__':
    '''back_up = GetbackUp()
    print('Backup process is started.')
    back_up.run_command()'''
    cisco_switches_backup = GetCiscoSwitchbackUp()
    GetCiscoSwitchbackUp.run_command(self=None)
    mikrotik_routers_backup = GetMikrotikbackUp()
    mikrotik_routers_backup.run_command()'''
    get_vlan_brief = GetVlanBrief()
    get_vlan_brief.run_command()

