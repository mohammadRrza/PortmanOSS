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
    username = ''
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
        count = 0
        for row in rows:
            count += 1
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
                params.username = row[0]
                params = json.dumps(params, default=lambda x: x.__dict__)
                result = utility.dslam_port_run_command(dslam_obj.pk, 'show linerate', json.loads(params))
                port_info = utility.dslam_port_run_command(dslam_obj.pk, 'port Info', json.loads(params))
                current_user_profile = ""
                for item in port_info['result']:
                    if 'prof' in item and 'alarm prof' not in item and 'profile' not in item:
                        current_user_profile = item.split(':')[1]
                payload_date_down = result['result']['payloadrateDown']
                attainable_rate_down = result['result']['attainablerateDown']
                print('+++++++++++++++++++++++++++')
                print(count)
                print('+++++++++++++++++++++++++++')
                table_name = '"16m_result"'
                query = "INSERT INTO public.{} VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(table_name,
                                                                                                         row[17].lower(),
                                                                                                         row[15],
                                                                                                         row[16],
                                                                                                         payload_date_down,
                                                                                                         row[0],
                                                                                                         current_user_profile,
                                                                                                         attainable_rate_down)
                print(query)
                cursor = connection.cursor()
                cursor.execute(query)

            except Exception as e:
                print(e)
                table_name = '"16m_result"'
                ex_query = "INSERT INTO public.{} VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(table_name,
                                                                                                            row[17].lower(),
                                                                                                            row[15],
                                                                                                            row[16], '',
                                                                                                            row[0], '',
                                                                                                            '')
                print(ex_query)
                cursor = connection.cursor()
                cursor.execute(ex_query)
