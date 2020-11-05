import telnetlib
import time
from .base_command import BaseCommand

class PortPvcDelete(BaseCommand):
    __slot__ = ('tn', 'port_indexes', 'fiberhomeAN2200_q', 'dslam_id')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.port_indexes = params.get('port_indexes')
        self.dslam_id = params.get('dslam_id')
        self.fiberhomeAN2200_q = fiberhomeAN2200_q

    def get_pvc_number(self, slot_number, port_number):
        tn.write("CORE\r\n".encode('utf-8'))
        tn.write("showvc\r\n".encode('utf-8'))
        tn.write("1\r\n".encode('utf-8'))
        tn.write("0-{0}-{1}\r\n".format(slot_number, port_number).encode('utf-8'))
        time.sleep(1)
        tn.read_until("PVC")
        return tn.read_until("CORE").split('\n\r')[1].split()[0]

    def run_command(self, protocol):
        self.tn.write("core\r\n".encode('utf-8'))
        # search on AD32+ type
        for port in self.port_indexes:
            self.tn.write("dvc\r\n".encode('utf-8'))
            self.tn.write("{0}\r\n".format(self.get_pvc_number(port['slot_number'], port['port_number'])).encode('utf-8'))
            time.sleep(1)
        result = {"result": "{0} port pvc set.". self.port_indexes}
        print('===================================')
        print(result)
        print('===================================')
        if protocol == 'http':
            return result
        elif protocol == 'socket':
            self.fiberhomeAN2200_q.put((
                "update_dslamport_command_result",
                self.dslam_id,
                self.port_indexes,
                "port pvc delete",
                result))

