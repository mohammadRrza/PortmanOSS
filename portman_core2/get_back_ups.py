import datetime
import os
import sys
import paramiko
from dj_bridge import Router, Switch


class GetbackUp():
    def __init__(self):
        pass

    def run_command(self):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            SwitchObjs = Switch.objects.all()
            for SwitchObj in SwitchObjs:
                try:
                    client.connect(SwitchObj.device_ip, username=SwitchObj.SSH_username, password=SwitchObj.SSH_password,
                                   port=1001, timeout=10,
                                   allow_agent=False,
                                   look_for_keys=False)
                    stdin, stdout, stderr = client.exec_command('show run')
                    f = open("/opt/portmanv3/portman_core2/switch_vendors/cisco_commands/Backups/{0}_{1}.txt".format(
                        SwitchObj.device_fqdn, str(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))), "w")
                    for line in stdout:
                        f.write(line.strip('\n'))
                    f.close()
                    client.close()
                except Exception as ex:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    f = open("/opt/portmanv3/portman_core2/switch_vendors/cisco_commands/Backups/Error_{0}_{1}.txt".format(
                        SwitchObj.device_fqdn, str(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))), "w")
                    f.write(str(ex) + "  // " + str(exc_tb.tb_lineno))
                    f.close()
                    client.close()

            RouterObjs = Router.objects.all()
            for RouterObj in RouterObjs:
                try:
                    '''print(RouterObj.device_ip+'  ' + RouterObj.SSH_username+' ' + RouterObj.SSH_password)'''
                    client.connect(RouterObj.device_ip, username=RouterObj.SSH_username, password=RouterObj.SSH_password,
                                   port=1001, timeout=10,
                                   allow_agent=False,
                                   look_for_keys=False)
                    stdin, stdout, stderr = client.exec_command('export verbose terse')
                    f = open("/opt/portmanv3/portman_core2/router_vendors/mikrotik_commands/Backups/{0}_{1}.txt".format(
                        RouterObj.device_fqdn, str(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))), "w")
                    for line in stdout:
                        f.write(line.strip('\n'))
                    f.close()
                    client.close()
                except Exception as ex:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    f = open("/opt/portmanv3/portman_core2/router_vendors/mikrotik_commands/Backups/Error_{0}_{1}.txt".format(
                        RouterObj.device_fqdn, str(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))), "w")
                    f.write(str(ex) + "  // " + str(exc_tb.tb_lineno))
                    f.close()
                    client.close()
            return ""
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return str(ex) + "  // " + str(exc_tb.tb_lineno)
