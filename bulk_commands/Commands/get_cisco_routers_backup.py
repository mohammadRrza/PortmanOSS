import datetime
import os
import sys
import paramiko
from django.db import connection
from django.http import JsonResponse
from pathlib import Path
from Commands.mail import Mail

class GetCiscoRouterbackUp():
    def __init__(self):
        pass

    def run_command(self):
        mail = Mail()
        mail.from_addr = 'oss-problems@pishgaman.net'
        mail.to_addr = 'oss-problems@pishgaman.net'
        mail.msg_subject = 'Get Device Backups'
        mail.msg_body = 'Cisco Router Backup Process has been started at {0}'.format(
            str(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
        # Mail.Send_Mail(mail)
        home = "/home/taher/"#str(Path.home())
        print("=============================================")
        print("Router Backup Process has been started...")
        print("=============================================")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        query = "SELECT Distinct  device_type, device_brand, device_ip, device_fqdn from zabbix_hosts where  (device_type = 'cisco_router' and device_brand = 'cisco') and device_fqdn NOT like  '%OLD%' ORDER BY device_ip"
        cursor = connection.cursor()
        cursor.execute(query)
        RouterObjs = cursor.fetchall()
        num = 0
        for RouterObj in RouterObjs:
            try:
                num = num+1
                print("=============================================")
                print(str(num)+'. '+RouterObj[2]+' '+RouterObj[3])
                print("=============================================")
                client.connect(RouterObj[2], username='backup-noc',
                               password='Yq*teoyg&fb@',
                               port=22, timeout=10,
                               allow_agent=False,
                               look_for_keys=False)
                stdin, stdout, stderr = client.exec_command('show run')
                f = open(home+"/backup/cisco_routers/{0}@{1}_{2}.txt".format(
                    RouterObj[3], RouterObj[2], str(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))), "w")
                stdin.flush()
                for line in stdout:
                    f.write(line.strip('\n'))
                f.close()
                client.close()

            except Exception as ex:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                f = open(home+"/backup/cisco_routers/Error_{0}@{1}_{2}.txt".format(
                    RouterObj[3], RouterObj[2], str(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))), "w")
                f.write(str(ex) + "  // " + str(exc_tb.tb_lineno))
                f.close()
                client.close()
                print(str(ex) + " " + str(exc_tb.tb_lineno))

        return ""
