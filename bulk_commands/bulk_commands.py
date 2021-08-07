from Commands.get_backups import GetbackUp
from Commands.get_mikrotik_routers_backup import GetMikrotikbackUp


if __name__ == '__main__':
    '''back_up = GetbackUp()
    print('Backup process is started.')
    back_up.run_command()'''
    mikrotik_routers_backup = GetMikrotikbackUp()
    mikrotik_routers_backup.run_command()