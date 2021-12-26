import datetime
import json
import os
import sys
from django.db import connection
from dj_bridge import utility
from dj_bridge import DSLAM


class port_condition2:
    slot_number = 0
    port_number = 0


class param2:
    command = ''
    type = ''
    is_queue = ''
    fqdn = ''
    slot_number = 0
    port_number = 0
    port_conditions = port_condition2()


class GetDslamPortParams:
    def __init__(self):
        pass

    def run_command(self):
        query = 'SELECT * from "16M_report" where fqdn is not null'
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            try:
                print(row[17])
                dslam_obj = DSLAM.objects.get(fqdn=row[17].lower())
                params = param2()
                params.type = 'dslamport'
                params.is_queue = False
                params.fqdn = dslam_obj.fqdn
                params.command = 'show linerate'
                params.port_conditions = port_condition2()
                params.port_conditions.slot_number = row[15]
                params.port_conditions.port_number = row[16]
                params = json.dumps(params, default=lambda x: x.__dict__)
                result = utility.dslam_port_run_command(dslam_obj.pk, 'show linerate', json.loads(params))
                print('+++++++++++++++++++++++++++')
                print(result['result']['payloadrateDown'])
                print('+++++++++++++++++++++++++++')
                table_name = '"16m_result"'
                query = "INSERT INTO public.{} VALUES ('{}', '{}', '{}', '{}')".format(table_name, row[17].lower(),
                                                                                       row[16], row[15],
                                                                                       result['result'][
                                                                                           'payloadrateDown'])
                print(query)
                cursor = connection.cursor()
                cursor.execute(query)

            except Exception as e:
                print(e)
                table_name = '"16m_result"'
                ex_query = "INSERT INTO public.{} VALUES ('{}', '{}', '{}', '{}')".format(table_name, row[17].lower(),
                                                                                          row[16], row[15],
                                                                                          str(e))
                print(ex_query)
                cursor = connection.cursor()
                cursor.execute(ex_query)
