import datetime
import os
import sys
import paramiko
from django.db import connection



class SetSSL():
    def __init__(self):
        pass

    def run_command(self):

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        query = "SELECT * from zabbix_hosts where device_fqdn like '%hsp%' and device_fqdn not like '%OLD%'"
        cursor = connection.cursor()
        cursor.execute(query)
        HspObjs = cursor.fetchall()
        num = 0
        for HspObj in HspObjs:
            try:
                client.close()

            except Exception as ex:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                client.close()
                print(str(ex) + " " + str(exc_tb.tb_lineno))

        return ""
