import datetime
import time

import paramiko
import sys, os
from .command_base import BaseCommand
import re


class SetRadioGeographicalCoordinates(BaseCommand):
    def __init__(self, params):
        self.__IP = params.get('router_ip')
        self.__SSH_username = params.get('SSH_username')
        self.__SSH_password = params.get('SSH_password')
        self.__SSH_port = params.get('SSH_port', 1001)
        self.__SSH_timeout = params.get('SSH_timeout', 10)
        self.Latitude = params.get('Latitude', 0)
        self.Longitude = params.get('Longitude', 0)
        self.__Command = "snmp set location=Latitude:{0}-Longitude:{1}".format(self.Latitude, self.Longitude)
        self.__FQDN = params.get('router_fqdn')

    def run_command(self):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.__IP, username=self.__SSH_username, password=self.__SSH_password, port=self.__SSH_port, timeout=self.__SSH_timeout, allow_agent=False, look_for_keys=False)
            stdin, stdout, stderr = client.exec_command(self.__Command)

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return str(ex) + "  // " + str(exc_tb.tb_lineno)
