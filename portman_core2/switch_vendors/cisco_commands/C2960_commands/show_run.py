import datetime
import os
import sys

import paramiko

from .command_base import BaseCommand


class ShowRun(BaseCommand):
    def __init__(self, params):
        self.__IP = '172.28.32.135'
        self.__SSH_username = 'developer'
        self.__SSH_password = 'developer'
        self.__Command = 'show run'

    def run_command(self):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.__IP, username=self.__SSH_username, password=self.__SSH_password, allow_agent=False,
                           look_for_keys=False)
            stdin, stdout, stderr = client.exec_command('show run')
            f = open("/opt/portmanv3/portman_core2/switch_vendors/cisco_commands/vlan_brief_Backups/{0}_{1}.txt".format(
                self.__IP, str(datetime.datetime)), "w")
            for line in stdout:
                f.write(line.strip('\n'))
            f.close()
            client.close()
            return "Ok"
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return str(ex) + "  // " + str(exc_tb.tb_lineno)
