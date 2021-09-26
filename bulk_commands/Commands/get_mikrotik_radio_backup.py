import datetime
import os
import sys
import paramiko
from django.db import connection
from django.http import JsonResponse
from pathlib import Path
import time
from Commands.mail import Mail


class GetMikrotikRadiobackUp():
    def __init__(self):
        pass

    def run_command(self):
        try:
            """mail = Mail()
            mail.from_addr = 'oss-problems@pishgaman.net'
            mail.to_addr = 'oss-problems@pishgaman.net'
            mail.msg_subject = 'Get Device Backups'
            mail.msg_body = 'Mikrotik Wireless Backup Process has been started at {0}'.format(
                str(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')))
            Mail.Send_Mail(mail)"""
            home = "/home/taher"  # str(Path.home())
            endtime = time.time() + 10
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            query = "SELECT Distinct  device_type, device_brand, device_ip, device_fqdn from zabbix_hosts where device_brand = 'mikrotik' and device_type = 'wireless' and device_fqdn NOT like  '%OLD%' ORDER BY device_ip"
            cursor = connection.cursor()
            cursor.execute(query)
            RadioObjs = cursor.fetchall()
            num = 0
            for RadioObj in RadioObjs:
                try:
                    num = num + 1
                    print("=====================Radio========================")
                    print(str(num) + '. ' + RadioObj[2] + ' ' + RadioObj[3])
                    print("==================================================")
                    client.connect(RadioObj[2], username='mik-backup',
                                   password='eS7*XiMmyeeU',
                                   port=1001, timeout=10,
                                   allow_agent=False,
                                   look_for_keys=False,
                                   banner_timeout=200)
                    stdin, stdout, stderr = client.exec_command('export verbose terse')

                    f = open(home + "/backup/mikrotik_radios/{0}@{1}_{2}.txt".format(
                        RadioObj[3], RadioObj[2], str(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))), "w")
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
                    f = open(home + "/backup/mikrotik_radios/Error_{0}@{1}_{2}.txt".format(
                        RadioObj[3], RadioObj[2], str(datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))), "w")
                    f.write(str(ex) + "  // " + str(exc_tb.tb_lineno))
                    f.close()
                    client.close()
            return ""

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(str(ex) + "  // " + str(exc_tb.tb_lineno))
            """mail = Mail()
            mail.from_addr = 'oss-problems@pishgaman.net'
            mail.to_addr = 'oss-problems@pishgaman.net'
            mail.msg_subject = 'Get Device Backups Error'
            mail.msg_body = 'Error: {0}----{1}'.format(str(ex), str(exc_tb.tb_lineno), )
            Mail.Send_Mail(mail)"""
