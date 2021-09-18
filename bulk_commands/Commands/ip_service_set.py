import sys
import paramiko
from django.db import connection



class SetIPService:
    def __init__(self):
        pass

    def run_command(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        query = "select DISTINCT * from zabbix_hosts where device_brand = 'mikrotik' and device_type = 'router_board' and device_fqdn NOT like  '%OLD%' ORDER BY device_ip"
        cursor = connection.cursor()
        cursor.execute(query)
        RouterObjs = cursor.fetchall()
        num = 0
        for RouterObj in RouterObjs:
            try:
                num = num + 1
                print("=============================================")
                print(str(num) + '. ' + RouterObj[2] + ' ' + RouterObj[3])
                print("=============================================")
                client.connect(RouterObj[2], username='mik-backup',
                               password='eS7*XiMmyeeU',
                               port=1001, timeout=10,
                               allow_agent=False,
                               look_for_keys=False,
                               banner_timeout=200)
                stdin, stdout, stderr = client.exec_command('ip service set numbers=3 address=172.28.238.114/32,109.125.191.0/24,5.202.129.0/24')
                client.close()
            except Exception as ex:
                print(str(ex) + " " + "35_mik")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(str(ex) + "  // " + str(exc_tb.tb_lineno))
        return ""
