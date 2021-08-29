from django.db import connection


class ZabbixHosts:
    def __init__(self):
        pass

    def get_zabbix_hosts(self):
        try:
            fd = open('Commands/insert_devices_from_zabbix.sql', 'r')
            sqlFile = fd.read()
            fd.close()
            query = sqlFile
            print(sqlFile)
            cursor = connection.cursor()
            cursor.execute(query)
            return 'Ok'
        except Exception as ex:
            print(ex)