import telnetlib
import time
import re
import sys
import os
from base_command import BaseCommand

class GetCurrentPortStatus(BaseCommand):
    __slot__ = ('tn', 'dslam_id', 'slot_number', 'port_number', 'fiberhomeAN2200_q')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.dslam_id = params.get('dslam_id')
        self.port_number = params.get('port_number')
        self.slot_number = params.get('slot_number')

    def get_atten_flag(self, atten_value):
        if atten_value <= 20:
            return 'outstanding'
        elif atten_value > 20  and atten_value <= 30 :
            return 'excellent'
        elif atten_value > 30 and atten_value <= 40 :
            return 'very_good'
        elif atten_value > 40 and atten_value <= 50 :
            return 'good'
        elif atten_value > 50 and atten_value <= 60 :
            return 'poor'
        else:
            return 'bad'

    def get_snr_flag(self, snr_value):
        if snr_value <= 6:
            return 'bad'
        elif snr_value > 6  and snr_value <= 10 :
            return 'fair'
        elif snr_value > 10 and snr_value <= 20 :
            return 'good'
        elif snr_value > 20 and snr_value <= 29 :
            return 'excellent'
        else:
            return 'outstanding'

    def run_command(self, protocol):
        port_info = {}
        port_event_items = []

        self.tn.write("line\r\n".encode('utf-8'))
        time.sleep(1)
        self.tn.write("\r\n".encode('utf-8'))
        self.tn.write("showport\r\n".encode('utf-8'))
        time.sleep(1)
        self.tn.write("0-{0}\r\n".format(self.slot_number).encode('utf-8'))
        time.sleep(1)
        self.tn.write("{0}\r\n".format(self.port_number).encode('utf-8'))
        self.tn.write("\r\n".encode('utf-8'))
        time.sleep(6)
        self.tn.write("end_of_line\r\n".encode('utf-8'))
        data = self.tn.read_until('end_of_line')
        try:
            record = re.compile('----------Shelf 0 ').split(data)[1]
            lines = record.split('\n\r')

            port_info['SLOT_NUMBER'] ,port_info['PORT_NUMBER'] = lines[0].split()[1::2]
            port_number = port_info['PORT_NUMBER'].strip()
            slot_number = port_info['SLOT_NUMBER'].strip()
            port_info['ORT_INDEX'] = '{0}{1:02}'.format(slot_number, int(port_number))
            port_info['PORT_ADMIN_STATUS'] = 'LOCK'
            port_info['PORT_OPER_STATUS'] = 'NO-SYNC'
            port_info['PORT_NAME'] = 'adsl{0}-{1}'.format(port_info['SLOT_NUMBER'], port_info['PORT_NUMBER'])
            for line in lines[1:]:
                if 'error' in line:
                    break

                if ':' in line:
                    key, value = map(str.strip, line.split(':'))
                    if 'OP_State' in key:
                        op_status = value.strip()
                        if op_status == 'data':
                            port_info['PORT_OPER_STATUS'] = 'SYNC'
                        else:
                            port_info['PORT_OPER_STATUS'] = 'NO-SYNC'
                    elif 'Stream SNR_Margin(D/U)' in key:
                        downstream_snr, upstream_snr = value.split()[0].split('/')
                        port_info['ADSL_UPSTREAM_SNR'] = upstream_snr.split()[0]
                        port_info['ADSL_DOWNSTREAM_SNR'] = downstream_snr.split()[0]
                        port_info['ADSL_UPSTREAM_SNR_FLAG'] = self.get_snr_flag(float(port_info['ADSL_UPSTREAM_SNR']) / 10)
                        port_info['ADSL_DOWNSTREAM_SNR_FLAG'] = self.get_snr_flag(float(port_info['ADSL_DOWNSTREAM_SNR']) / 10)
                    elif 'Stream attenuation(D/U)' in key:
                        downstream_atten, upstream_atten = value.split()[0].split('/')
                        port_info['ADSL_UPSTREAM_ATTEN'] = upstream_atten.split()[0]
                        port_info['ADSL_DOWNSTREAM_ATTEN'] = downstream_atten.split()[0]
                        port_info['ADSL_UPSTREAM_ATTEN_FLAG'] = self.get_atten_flag(float(port_info['ADSL_UPSTREAM_ATTEN']) / 10)
                        port_info['ADSL_DOWNSTREAM_ATTEN_FLAG'] = self.get_atten_flag(float(port_info['ADSL_DOWNSTREAM_ATTEN']) / 10)

                    elif 'Attainable rate(D/U)' in key:
                        downstream_atten, upstream_atten = value.split()[0].split('/')
                        port_info['ADSL_DOWNSTREAM_ATT_RATE'] = downstream_atten.split()[0]
                        port_info['ADSL_UPSTREAM_ATT_RATE'] = upstream_atten.split()[0]
                    elif 'Tx power(D/U)' in key:
                        downstream_att_rate, upstream_att_rate = value.split()[0].split('/')
                        port_info['ADSL_CURR_DOWNSTREAM_RATE'] = downstream_att_rate.split()[0]
                        port_info['ADSL_CURR_UPSTREAM_RATE'] = upstream_att_rate.split()[0]
            self.tn.write("showportcfg\r\n".encode('utf-8'))
            time.sleep(1)
            self.tn.write("0-{0}\r\n".format(self.slot_number).encode('utf-8'))
            time.sleep(1)
            self.tn.write("\r\n".format(self.port_number).encode('utf-8'))
            self.tn.write("\r\n".encode('utf-8'))
            time.sleep(3)
            self.tn.write("end_of_line\r\n".encode('utf-8'))
            data = self.tn.read_until('end_of_line')
            try:
                lines = re.compile("-----------------SHELF\sNUM\s0--CARD\sNUM\s").split(data)[1]
                com = re.compile(r'\s+(?P<port_number>\d+)\s+(?P<PORT_ADMIN_STATUS>\w+)\s+\S+\s+\S+\s+\S+\s+\d+(\s)?/(\s)?\d+\s+\d+(\s)?/(\s)?\d+\s+(?P<LINE_PROFILE>\S+)')
                rows = [m.groupdict() for m in com.finditer(lines)]
                for row in rows:
                    if str(row.get('port_number')) == str(self.port_number):
                        port_info['LINE_PROFILE'] = row['LINE_PROFILE']
                        if str(row['PORT_ADMIN_STATUS']) == 'OPEN':
                            port_info['PORT_ADMIN_STATUS'] = 'UNLOCK'
                        else:
                            port_info['PORT_ADMIN_STATUS'] = 'LOCK'
                        break

            except:
                #print data
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                #print exc_type, fname, exc_tb.tb_lineno
                port_event_items.append({
                    "event": "Don't give Result",
                    "message": "error on PORT_ADMIN_STATUS"
                    })



        except Exception as ex:
            #print data
            port_event_items.append({
                "event": "Don't give Result",
                "message": "error on Get Current Port Status"
                })
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #print(exc_type, fname, exc_tb.tb_lineno)

        result = {'port_current_status': port_info, 'port_events': {'dslam_id': self.dslam_id, 'slot_number': self.slot_number, 'port_number': self.port_number, 'port_event_items': port_event_items}}

        #print '-----------------------------------'
        #print result
        #print '-----------------------------------'

        if protocol == 'http':
            return result
        elif protocol == 'socket':
            self.fiberhomeAN2200_q.put((
                "update_port_status",
                self.dslam_id,
                "show time",
                result
                ))
