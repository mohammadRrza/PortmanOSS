import telnetlib
import traceback
import time
from socket import error as socket_error
import re
import telnetlib
import re
from .base_command import BaseCommand

class GetCurrentPortStatus(BaseCommand):
    __slot__ = ('tn', 'fiberhomeAN3300_q', 'slot_number', 'port_number' , 'dslam_id')
    def __init__(self, tn, params, fiberhomeAN3300_q=None):
        self.tn = tn
        self.fiberhomeAN3300_q = fiberhomeAN3300_q
        self.port_number = params.get('port_number')
        self.dslam_id = params.get('dslam_id')
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
        port_event_items = []
        self.tn.write(("cd device\r\n").encode('utf-8'))
        data = self.tn.read_until("#")
        self.tn.write("show port {0}:{1} configuration\r\n".format(self.slot_number, self.port_number).encode('utf-8'))
        time.sleep(1)
        self.tn.write("\r\n".encode('utf-8'))
        time.sleep(1)
        data = self.tn.read_until("#")
        print('++++++++++++++++++++++++++++++++++++++++++++++')
        print(data)
        print('++++++++++++++++++++++++++++++++++++++++++++++')
        port = {}
        try:
            port['SLOT_NUMBER'], port['PORT_NUMBER'] = re.search('show\sport\s(\d+)\:(\d+)\sconfiguration', data).groups()
            port['PORT_NAME'] = 'adsl{0}-{1}'.format(port['SLOT_NUMBER'], port['PORT_NUMBER'])
            port['PORT_INDEX'] = '{0}{1:02}'.format(port['SLOT_NUMBER'], int(port['PORT_NUMBER']))

            link_state = re.search('Link\sstate\s*:\s(\S+)', data).groups()[0]
            if link_state == 'Up':
                port['PORT_OPER_STATUS'] = 'SYNC'
            else:
                port['PORT_OPER_STATUS'] = 'NO-SYNC'

            port_state = re.search('Port\sstate\s*:\s(\S+)', data).groups()[0]
            if port_state == 'Enable':
                port['PORT_ADMIN_STATUS'] = 'UNLOCK'
            else:
                port['PORT_ADMIN_STATUS'] = 'LOCK'

            op_state = None
            try:
                op_state = re.search('OP\sState\s*:\s(\S+)', data).groups()[0]
            except:
                port_vlan_id = re.search('Port\sVLAN\sID\s*:\s(\S+)', data).groups()[0]
                port_vlan_name = re.search('Port\sVLAN\sname\s*:\s(\S+)', data).groups()[0]

            if op_state:
                port['LINE_PROFILE'] = re.search('Profile\sName\s*:\s(\S+)', data).groups()[0]
                if op_state == 'DATA' and link_state == 'Up':
                    downstream_rate = re.search('DownStream\srate\s*:\s(\S+)', data).groups()[0]
                    upstream_rate = re.search('UpStream\srate\s*:\s(\S+)', data).groups()[0]
                    port['ADSL_DOWNSTREAM_ATT_RATE'] = re.search('DownStream\sattain\srate\s*:\s(\S+)', data).groups()[0] #downstream_attain_rate
                    port['ADSL_UPSTREAM_ATT_RATE'] = re.search('UpStream\sattain\srate\s*:\s(\S+)', data).groups()[0] #upstream_attain_rate
                    port['ADSL_DOWNSTREAM_ATTEN'] = re.search('DownStream\sAttenuat\s*:\s(\S+)', data).groups()[0] #dwonstream_margin
                    port['ADSL_UPSTREAM_ATTEN'] = re.search('UpStream\sAttenuat\s*:\s(\S+)', data).groups()[0]
                    port['ADSL_CURR_DOWNSTREAM_RATE'] = re.search('DownStream\sTx\sPower\s*:\s(\S+)', data).groups()[0] #downstream_tx_power
                    port['ADSL_CURR_UPSTREAM_RATE'] = re.search('UpStream\sTx\sPower\s*:\s(\S+)', data).groups()[0] #upstream_tx_power
                    port['ADSL_DOWNSTREAM_SNR'] = re.search('DownStream\sMargin\s*:\s(\S+)', data).groups()[0]
                    port['ADSL_UPSTREAM_SNR'] = re.search('UpStream\sMargin\s*:\s(\S+)', data).groups()[0] #downstream_margin
                    port['ADSL_UPSTREAM_SNR_FLAG'] =  self.get_snr_flag(float(port['ADSL_UPSTREAM_SNR']) /10)
                    port['ADSL_DOWNSTREAM_SNR_FLAG'] =  self.get_snr_flag(float(port['ADSL_DOWNSTREAM_SNR']) /10)
                    port['ADSL_UPSTREAM_ATTEN_FLAG'] = self.get_atten_flag(float(port['ADSL_UPSTREAM_ATTEN']) /10)
                    port['ADSL_DOWNSTREAM_ATTEN_FLAG'] = self.get_atten_flag(float(port['ADSL_DOWNSTREAM_ATTEN']) /10)

                    downstream_int_delay = re.search('DownStream\sInt\sDelay\s+:\s(\S+)', data).groups()[0] #upstream_margin
                    upstream_int_delay = re.search('UpStream\sInt\sDelay\s+:\s(\S+)', data).groups()[0]

        except Exception as ex:
            import sys
            import os
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(traceback.format_exc())
            print(exc_type, fname, exc_tb.tb_lineno)
            port_event_items.append({
                "event": "Don't give Result",
                "message": "error on get current port status command"
            })



        result = {'port_current_status': port, 'port_events': {'dslam_id': self.dslam_id, 'slot_number': self.slot_number, 'port_number': self.port_number, 'port_event_items': port_event_items}}

        if protocol == 'http':
            return result
        elif protocol == 'socket':
            self.fiberhomeAN2200_q.put((
                "update_port_status",
                self.dslam_id,
                "show time",
                result
            ))

