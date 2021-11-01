import datetime
import os
import sys

import requests
from django.db import connection
from django.http import JsonResponse
from requests import Response
from rest_framework import status


class ZabbixHosts:
    def __init__(self):
        pass

    def get_zabbix_hosts(self):
        try:
            i=0
            zabbix_url = 'https://monitoring1.pishgaman.net/api_jsonrpc.php'
            zabbix_login_data = '{"jsonrpc": "2.0","method": "user.login","params": {"user": "software","password": "ASXRQKD78kykRLT"},"id": 1,"auth": null}'
            response = requests.post(zabbix_url, data=zabbix_login_data, headers={"Content-Type": "application/json"})
            login = response.json()
            token = login['result']
            select_query = "DELETE from zabbix_hosts;SELECT * FROM zabbix_hostgroups"
            cursor = connection.cursor()
            cursor.execute(select_query)
            rows = cursor.fetchall()
            for row in rows:
                zabbix_get_host_data = '{"jsonrpc": "2.0","method": "host.get","params": {"groupids":["%s"],"output": ["hostid","host"],"selectInterfaces": ["ip"]},"id": 1,"auth": "%s"}'% (row[0], token)
                host_response = requests.post(zabbix_url, data=zabbix_get_host_data,
                                              headers={"Content-Type": "application/json"})
                hosts = host_response.json()
                # return JsonResponse({'hosts':hosts['result'] })
                switch_types = ["c2960", "4948", "c9200", "c3064pq"]
                switch_layer3 = ["c3850", "c3750", "c4500", "c4500x", "c6816x", "c6840x"]
                router = ["9500", "c2921k9", "asr1002x", "asr1002", "asr1002hx", "asr1001x"]
                router_board = ["RB450G", "RB450", "RB750Gr3", "RB750R2", "CCR1009", "RB1100", "CCR1016", "CCR1036",
                                "hEX", "RB1100AHx2","1100AHx2", "RB1100AH", "RB1100x4", "RB1100AHx4","RB2011", "RB433AH", "RB433ah", "hEXRB750",
                                "750Gr3hEX", "RB3011UiAS", "HexRB750", "hex"]
                router_virtual = ["vmx86", "vmx86"]
                switch_board = ["CRS328", "CRS125"]
                wireless = ["LHG5", "LHGHP", "LHG", "LHGXL", "LHG HP5", "SXThpnd", "RB911G-5", "LHGXL5", "B921UA",
                            "RB921UAGS", "Netmetal5", "NetMetal", "Metal5", "metal5", "SXT", "SXTLite5", "SXT5", "SXT6",
                            "Mimosa", "GrooveA52", "MANTBox", "Groove52HPnr2", "MimosaB5C", "RBSXT", "Sextant",
                            "RB411AH", "Groove", "Groove5", "Groove52", "QRT", "QRT5", "DynaDish5", "daynadish5",
                            "Daynadish5", "OmniTIK5", "Netbox", "Netbox5", "RB912UAG", "RB411G", "BaseBox", "RBLHG5",
                            "BaseBox5", "Sextant5", "RB911G", "RBSXT", "SXTSQ5", "921UA", "912UAG", "RB921GS",
                            "RBmetal"]
                engenius_switch = ["EWS1200"]
                engenius_wap = ["UBNT", "EWS310AP"]
                zyxel_dslam = ["Z6000", "z6000"]
                fiberhome_dslam = ["AN2200a", "AN3300", "AN5006", "an2200a", "an3300", "an5006", "AN5006a", "an5006a"]
                huawei_dslam = ["huawei5600", "MA5616"]

                for item in hosts['result']:
                    # return JsonResponse({'hosts':item['host'].split('.')[5] })
                    try:
                        if (item['host'].split('.')[5].lower() in [x.lower() for x in switch_types] or
                                item['host'].split('.')[4].lower() in [x.lower() for x in switch_types]):
                            device_type = "switch"
                            device_brand = "cisco"
                        elif (item['host'].split('.')[5].lower() in [x.lower() for x in switch_layer3] or
                              item['host'].split('.')[4].lower() in [x.lower() for x in switch_layer3]):
                            device_type = "switch_layer3"
                            device_brand = "cisco"
                        elif (item['host'].split('.')[5].lower() in [x.lower() for x in router] or
                              item['host'].split('.')[4].lower() in [x.lower() for x in router]):
                            device_type = "router"
                            device_brand = "cisco"
                        elif (item['host'].split('.')[5].lower() in [x.lower() for x in router_board] or
                              item['host'].split('.')[4].lower() in [x.lower() for x in router_board]):
                            device_type = "router_board"
                            device_brand = "mikrotik"
                        elif (item['host'].split('.')[5].lower() in [x.lower() for x in router_virtual] or
                              item['host'].split('.')[4].lower() in [x.lower() for x in router_virtual]):
                            device_type = "router_virtual"
                            device_brand = "mikrotik"
                        elif (item['host'].split('.')[5].lower() in [x.lower() for x in switch_board] or
                              item['host'].split('.')[4].lower() in [x.lower() for x in switch_board]):
                            device_type = "switch_board"
                            device_brand = "mikrotik"
                        elif (item['host'].split('.')[5].lower() in [x.lower() for x in wireless] or
                              item['host'].split('.')[4].lower() in [x.lower() for x in wireless]):
                            device_type = "wireless"
                            device_brand = "mikrotik"
                        elif (item['host'].split('.')[5].lower() in [x.lower() for x in engenius_switch] or
                              item['host'].split('.')[4].lower() in [x.lower() for x in engenius_switch]):
                            device_type = "engenius_switch"
                            device_brand = "Engenius"
                        elif (item['host'].split('.')[5].lower() in [x.lower() for x in engenius_wap] or
                              item['host'].split('.')[4].lower() in [x.lower() for x in engenius_wap]):
                            device_type = "engenius_wap"
                            device_brand = "Engenius"
                        elif (item['host'].split('.')[5].lower() in zyxel_dslam or item['host'].split('.')[
                            4].lower() in zyxel_dslam):
                            device_type = "dslam"
                            device_brand = "zyxel"
                        elif '2200' in item['host'] or '3300' in item['host'] or '5006' in item['host']:
                            device_type = "dslam"
                            if '2200' in item['host']:
                                device_brand = "fiberhome2200"
                            if '3300' in item['host']:
                                device_brand = "fiberhome3300"
                            if '5006' in item['host']:
                                device_brand = "fiberhome5006"
                        elif (item['host'].split('.')[5].lower() in huawei_dslam or item['host'].split('.')[
                            4].lower() in huawei_dslam):
                            device_type = "dslam"
                            device_brand = "huawei"
                        else:
                            device_type = "unknown"
                            device_brand = "unknown"
                        query = "INSERT INTO zabbix_hosts values('{0}','{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(
                            int(item['hostid']),
                            row[0],
                            item['interfaces'][0]['ip'], item['host'], datetime.datetime.now(), device_type, device_brand)

                        cursor = connection.cursor()
                        cursor.execute(query)

                    except Exception as ex:
                        if 'list index out of range' in str(ex):
                            query = "INSERT INTO zabbix_hosts values('{0}','{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(
                                int(item['hostid']),
                                row[0],
                                item['interfaces'][0]['ip'], item['host'], datetime.datetime.now(), str(ex), 'ERROR')
                            cursor = connection.cursor()
                            cursor.execute(query)
            fd = open('Commands/insert_devices_from_zabbix.sql', 'r')
            sqlFile = fd.read()
            fd.close()
            query = sqlFile
            cursor = connection.cursor()
            cursor.execute(query)
            return JsonResponse({'hosts': "OK"})
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(ex, str(exc_tb.tb_lineno))


