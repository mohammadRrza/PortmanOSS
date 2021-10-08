import telnetlib
from .base_command import BaseCommand
import time
import re

class UpLinkPvcDelete(BaseCommand):
    __slot__ = ('tn', 'dslam_id', 'fiberhomeAN2200_q', 'port_indexes')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.dslam_id = params.get('dslam_id')
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.port_indexes = params.get('port_indexes')

    def run_command(self, protocol):
        self.tn.write("core\r\n".encode('utf-8'))
        self.tn.write("showvc\r\n".encode('utf-8'))
        self.tn.read_until("showvc")
        self.tn.write('1\r\n'.encode('utf-8'))
        output = ''
        pvc_numbers = []
        for port in self.port_indexes:
            self.tn.write('0-{0}-{1}\r\n'.format(port.get('slot_number'), port.get('port_number')).encode('utf-8'))
            output = self.tn.read_until(">", 5)
            pvc_number = re.search(r'\s+(\d+)\s+\S+\s+\d+-\s?\d+-\s?\d+\s+\d+/\s?\d+\s+\d+-\s?\d+-\s?\d+\s+\d+/\s?\d+\s+\S+', output, re.M).groups()[0]
            pvc_numbers.append(pvc_number)


        for pvc_number in pvc_numbers:
            output = self.tn.read_until(">", 5)
            self.tn.write("deletevc\r\n".encode('utf-8'))
            self.tn.write("{0}\r\n".format(pvc_number).encode('utf-8'))
            result = {"result": "uplink {0} pvc is deleted".format(pvc_number)}

        if protocol == "http":
            return result
        elif protocol == "socket":
            self.fiberhomeAN2200_q.put(("update_dslam_command_result",
                self.dslam_id,
                "uplink pvc delete",
                result))

