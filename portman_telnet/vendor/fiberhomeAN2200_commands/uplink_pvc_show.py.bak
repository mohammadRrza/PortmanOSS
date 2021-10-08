import telnetlib
import time
from base_command import BaseCommand
class UpLinkPvcShow(BaseCommand):
    __slot__ = ('tn', 'dslam_id', 'fiberhomeAN2200_q', 'slot_number', 'port_indexes')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.dslam_id = params.get('dslam_id')
        self.slot_number = params.get('slot_number')
        self.port_indexes = params.get('port_indexes')

    def run_command(self, protocol):
        self.tn.write("core\r\n".encode('utf-8'))
        self.tn.write("showvc\r\n".encode('utf-8'))
        self.tn.read_until("showvc")
        self.tn.write('1\r\n'.encode('utf-8'))
        output = ''
        if self.slot_number:
            self.tn.write('0-{0}\r\n'.format(self.slot_number).encode('utf-8'))
            output = self.tn.read_until(">", 5)
            result = {'result': output}
        elif self.port_indexes:
            results = []
            for port in self.port_indexes:
                self.tn.write('0-{0}-{1}\r\n'.format(port.get('slot_number'), port.get('port_number')).encode('utf-8'))
                output = self.tn.read_until(">", 5)
                results.append(output)
            result = {'result': results}

        if protocol == "http":
            return result
        elif protocol == "socket":
            self.fiberhomeAN2200_q.put(("update_dslam_command_result",
                self.dslam_id,
                "uplink pvc show",
                result))
