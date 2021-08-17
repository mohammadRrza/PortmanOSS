import datetime
import os
import sys
import paramiko
from django.db import connection
from django.http import JsonResponse
from pathlib import Path
import time

class GetMikrotikbackUp():
    def __init__(self):
        pass

    def run_command(self):
        home = "/home/taher"#str(Path.home())
        endtime = time.time() + 10
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        query = "select * from zabbix_hosts where device_brand = 'mikrotik' and device_type = 'router_board'"
        cursor = connection.cursor()
        cursor.execute(query)
        RouterObjs = cursor.fetchall()
        num = 0
        for RouterObj in RouterObjs:
            try:
                num = num+1
                print("=============================================")
                print(str(num)+'. '+RouterObj[2])
                print("=============================================")
                client.connect(RouterObj[2], username='mik-backup',
                               password='eS7*XiMmyeeU',
                               port=1001, timeout=10,
                               allow_agent=False,
                               look_for_keys=False)
                stdin, stdout, stderr = client.exec_command('export verbose terse')

                f = open(home+"/backup/mikrotik_routers/{0}_{1}.txt".format(
                    RouterObj[2], str(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))), "w")
                while not stdout.channel.eof_received:
                    time.sleep(1)
                    if time.time() > endtime:
                        stdout.channel.close()
                        break
                for line in iter(lambda: stdout.readline(2048), ""):
                    f.write(line.strip('\n'))
                f.close()
                client.close()
            except Exception as ex:
                print(str(ex) + " " + "35_mik")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                f = open(home+"/backup/mikrotik_routers/Error_{0}_{1}.txt".format(
                    RouterObj[2], str(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))), "w")
                f.write(str(ex) + "  // " + str(exc_tb.tb_lineno))
                f.close()
                client.close()
        return ""
