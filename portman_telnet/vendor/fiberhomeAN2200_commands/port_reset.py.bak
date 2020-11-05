import telnetlib
import time
from base_command import BaseCommand

class PortReset(BaseCommand):
    __slot__ = ('tn', 'port_indexes', 'dslam_id', 'fiberhomeAN2200_q')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.dslam_id = params.get('dslam_id')
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.port_indexes = params.get('port_indexes')

    def run_command(self, protocol):
        self.tn.write("line\r\n".encode('utf-8'))
        for port in self.port_indexes:
            self.tn.write("closeport\r\n".encode('utf-8'))
            self.tn.write("0-{0}\r\n".format(port['slot_number']).encode('utf-8'))
            time.sleep(1)
            self.tn.write("{0}\r\n".format(port['port_number']).encode('utf-8'))
            time.sleep(1)

            self.tn.write("openport\r\n".encode('utf-8'))
            self.tn.write("0-{0}\r\n".format(port['slot_number']).encode('utf-8'))
            time.sleep(1)
            self.tn.write("{0}\r\n".format(port['port_number']).encode('utf-8'))
            time.sleep(1)

        print '==================================='
        print {"result": "Reset port."}
        print '==================================='

        result = {"result": "Reset port"}
        if protocol == 'http':
            return result
        elif protocl == 'socket':
            self.fiberhomeAN2200_q.put((
                "update_dslamport_command_result",
                self.dslam_id,
                self.port_indexes,
                "port enable",
                result
                ))
