import datetime
import os
import sys

import paramiko

from .command_base import BaseCommand


class ShowRun(BaseCommand):
    def __init__(self, params):
        self.__IP = params.get('switch_ip')
        self.__SSH_username = params.get('SSH_username')
        self.__SSH_password = params.get('SSH_password')
        self.__SSH_port = params.get('SSH_port', 1001)
        self.__Command = 'show run'
        self.__FQDN = params.get('switch_fqdn')

    def run_command(self):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.__IP, username=self.__SSH_username, password=self.__SSH_password, port=self.__SSH_port, timeout=30, allow_agent=False,
                           look_for_keys=False)
            stdin, stdout, stderr = client.exec_command('show run')
            f = open("/opt/portmanv3/portman_core2/switch_vendors/cisco_commands/Backups/{0}_{1}.txt".format(
                self.__FQDN, str(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))), "w")
            for line in stdout:
                f.write(line.strip('\n'))
            f.close()
            client.close()
            return "Backup File named Backups/{0}_{1}.txt has been created.".format(self.__FQDN, str(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return str(ex) + "  // " + str(exc_tb.tb_lineno)
