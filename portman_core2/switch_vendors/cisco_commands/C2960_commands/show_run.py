import paramiko
import sys, os
from .command_base import BaseCommand
import re


class ShowRun(BaseCommand):
    def __init__(self, params):
        pass


    def run_command(self):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect("172.28.32.135", username="developer", password="developer", allow_agent=False, look_for_keys=False)
            stdin, stdout, stderr = client.exec_command('show run')
            f = open("/opt/portmanv3/portman_core2/switch_vendors/cisco_commands/Backups/172.28.32.135.txt", "w")
            for line in stdout:
                f.write(line.strip('\n'))
            f.close()
            client.close()
            return "Ok"
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return str(ex) + "  // " + str(exc_tb.tb_lineno)
