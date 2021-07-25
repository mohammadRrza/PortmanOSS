import datetime

import paramiko
import sys, os
from .command_base import BaseCommand
import re


class ApplyPermission(BaseCommand):
    def __init__(self, params):
        self.__IP = params.get('router_ip')
        self.__SSH_username = params.get('SSH_username')
        self.__SSH_password = params.get('SSH_password')
        self.__SSH_port = params.get('SSH_port', 1001)
        self.__SSH_timeout = params.get('SSH_timeout', 10)
        self.__Command = 'ip service set numbers=3 address=172.28.238.112/29,109.125.191.0/24,5.202.129.0/24'
        self.__FQDN = params.get('router_fqdn')

    def run_command(self):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.__IP, username=self.__SSH_username, password=self.__SSH_password, port=self.__SSH_port, timeout=self.__SSH_timeout, allow_agent=False, look_for_keys=False)
            stdin, stdout, stderr = client.exec_command(self.__Command)
            client.close()
            return "Ok"
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return str(ex) + "  // " + str(exc_tb.tb_lineno)
