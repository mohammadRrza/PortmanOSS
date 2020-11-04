import time
from datetime import datetime,timedelta
import logging
from datetime import datetime
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
from vendors.base import BaseDSLAM
from easysnmp import Session
from easysnmp import snmp_get, snmp_set, snmp_walk
import re
from collections import OrderedDict
log = logging.getLogger('portman')

class Zyxel(BaseDSLAM):

    PORT_DETAILS_OID_TABLE = {
        "1.3.6.1.2.1.1.3.0" : "sysUpTime",
        "1.3.6.1.2.1.1.5.0" : "Hostname",
        "1.3.6.1.2.1.1.1.0" : "Version",
        "1.3.6.1.4.1.890.1.5.13.5.11.3.3.1.6":"lineCardTempName",
        "1.3.6.1.4.1.890.1.5.13.5.11.3.3.1.2":"lineCardTempValue",
        "1.3.6.1.4.1.890.1.5.13.5.11.3.3.1.5":"temperatureHighThresh",
    }

    PORT_DETAILS_OID_TABLE_INVERSE = dict(list(zip(list(PORT_DETAILS_OID_TABLE.values()),list(PORT_DETAILS_OID_TABLE.keys()))))

    EVENT = {'get_dslam_sysUpTime_error':'Get DSLAM Uptime Error', 'get_dslam_temperature_error': 'Get DSLAM Temperature Error', 'get_dslam_hostname_error':'Get DSLAM Hostname Error', }
    EVENT_INVERS = dict(list(zip(list(EVENT.values()),list(EVENT.keys()))))

    @classmethod
    def translate_event_by_text(cls, event):
        if event in cls.EVENT_INVERS:
            return cls.EVENT_INVERS[event]
        return None

    @classmethod
    def get_dslam_status(cls, dslam_info):
        start = time.time()
        status_results = dict()

        version, uptime, hostname = cls.get_dslam_info(dslam_info)
        status_results['uptime'] = uptime
        status_results['hostname'] = hostname
        status_results['version'] = version
        status_results['line_card_temp'] = cls.get_line_card_temp(dslam_info)

        du = time.time() - start
        status_results['duration_time'] = du
        return status_results


    @classmethod
    def get_dslam_info(cls, dslam_data):
        dslam_ip = dslam_data['ip']
        snmp_community = dslam_data['get_snmp_community']
        snmp_port = int(dslam_data.get('snmp_port', 161))
        snmp_timeout = int(dslam_data.get('snmp_timeout', 5))
        uptime = ''
        version = ''
        try:
            session = Session(hostname=dslam_ip, community=snmp_community, remote_port=snmp_port,timeout=snmp_timeout, retries=1, version=2)

            version = session.get(cls.PORT_DETAILS_OID_TABLE_INVERSE['Version']).value

            hostname = {}
            try:
                hostname['value'] = session.get(cls.PORT_DETAILS_OID_TABLE_INVERSE['Hostname']).value
            except Exception as ex:
                hostname['event'] = cls.translate_event_by_text('Get DSLAM Hostname Error')
                hostname['message'] = 'SNMP for get hostname is not working'
                print('Give error from dslam :',dslam_data['id'], dslam_data['ip'] , dslam_data['get_snmp_community'])
                hostname['value'] = 'error'

            uptime = {}
            try:
                sys_up_time = session.get(cls.PORT_DETAILS_OID_TABLE_INVERSE['sysUpTime'])
                seconds = int(sys_up_time.value) / 100
                uptime['value'] = "{:0>8}".format(timedelta(seconds=seconds))
            except Exception as ex:
                uptime['event'] = cls.translate_event_by_text('Get DSLAM Uptime Error')
                uptime['message'] = 'SNMP for get sysUpTime is not working'
                uptime['value'] = 'error'
                print('Give error from dslam :',dslam_data['id'], dslam_data['ip'] , dslam_data['get_snmp_community'])
        except Exception as ex:
            print('=>>>>>>>>>>>>>>>>', ex)
            return None, None, None
        return (version, uptime, hostname)

    @classmethod
    def get_line_card_temp(cls, dslam_info):
        dslam_ip = dslam_info['ip']
        snmp_community = dslam_info['get_snmp_community']
        snmp_port = int(dslam_info.get('snmp_port', 161))

        session = Session(hostname=dslam_ip, community=snmp_community, remote_port=snmp_port,timeout=5, retries=3,version=2)
        lst_result = []
        try:
            card_temp_names = session.walk(cls.PORT_DETAILS_OID_TABLE_INVERSE['lineCardTempName'])
            oid_dict = {}
            for item in card_temp_names:
                oid_dict[item.oid]={'name':item.value}

            card_temp_names = session.walk(cls.PORT_DETAILS_OID_TABLE_INVERSE['lineCardTempValue'])

            for item in card_temp_names:
                oid_arr = item.oid.split('.')
                #convert name oid to value oid for find item using oid as key
                oid_arr[-4] = '6'
                oid = '.'.join(oid_arr)
                oid_dict[str(oid)]['CurValue'] = item.value

            card_temp_names = session.walk(cls.PORT_DETAILS_OID_TABLE_INVERSE['temperatureHighThresh'])
            for item in card_temp_names:
                oid_arr = item.oid.split('.')
                #convert name oid to value oid for find item using oid as key
                oid_arr[-4] = '6'
                oid = '.'.join(oid_arr)
                oid_dict[str(oid)]['HighThresh'] = item.value

            oid_dict = OrderedDict(sorted(list(oid_dict.items()), key=lambda t: t[0]))
            for item in oid_dict.values():
                lst_result.append(item)
        except:
            print('Give error from dslam :',dslam_info['id'], dslam_info['ip'] , dslam_info['get_snmp_community'])
        finally:
            result = {}
            if len(lst_result) == 0:
                result['event'] = cls.translate_event_by_text('Get DSLAM Temperature Error')
                result['message'] = 'SNMP for get DSLAM Line Cards Temperature is not working'
            result['value'] = lst_result
            return result

