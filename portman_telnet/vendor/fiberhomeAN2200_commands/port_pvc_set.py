import telnetlib
import time
from .base_command import BaseCommand

class PortPvcSet(BaseCommand):
    __slot__ = ('tn', 'port_vpi', 'port_vci', 'start_slot_number', 'start_port_number',\
            'wan_slot_number', 'wan_port_number', 'wan_vpi', 'wan_vci', 'vc_number', \
            'fiberhomeAN2200_q', 'dslam_id')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.dslam_id = params.get('dslam_id')
        self.port_vpi = params.get('port_vpi')
        self.port_vci = params.get('port_vci')
        self.start_slot_number = params.get('start_slot_number')
        self.start_port_number = params.get('start_port_number')
        self.wan_slot_number = params.get('wan_slot_number')
        self.wan_port_number = params.get('wan_port_number')
        self.wan_vpi = params.get('wan_vpi')
        self.wan_vci = params.get('wan_vci')
        self.vc_number = params.get('vc_number')
        self.fiberhomeAN2200_q = fiberhomeAN2200_q

    def run_command(self, protocol):
        self.tn.write("core\r\n".encode('utf-8'))
        # search on AD32+ type
        self.tn.write("looptowanvc\r\n".encode('utf-8'))
        time.sleep(1)
        self.tn.write("0-{0}-{1}\r\n".format(self.start_slot_number, self.start_port_number).encode('utf-8'))
        time.sleep(1)
        self.tn.write("{0}/{1}\r\n".format(self.port_vpi, self.port_vci).encode('utf-8'))
        time.sleep(1)
        self.tn.write("0-{0}-{1}\r\n".format(self.wan_slot_number, self.wan_port_number).encode('utf-8'))
        time.sleep(1)
        self.tn.write("{0}/{1}\r\n".format(self.wan_vpi, self.wan_vci).encode('utf-8'))
        time.sleep(1)
        self.tn.write("{0}\r\n".format(self.vc_number).encode('utf-8'))
        time.sleep(1)
        self.tn.write("0\r\n".encode('utf-8'))
        time.sleep(1)
        self.tn.read_until('looptowanvc', 5)
        result = self.tn.read_until('>', 5)
        print('===================================')
        print({"result": result})
        print('===================================')
        if protocol == 'http':
            return {"result": result}
        elif protocol == 'socket':
            self.fiberhomeAN2200_q.put(("update_dslamport_command_result",
                self.dslam_id,
                self.port_indexes,
                "port enable",
                result))


