import telnetlib
import time
from base_command import BaseCommand
class OpenPortSelt(BaseCommand):
    __slot__ = ('tn', 'port_indexes', 'fiberhomeAN2200_q', 'dslam_id')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.dslam_id = params.get('dslam_id')
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.tn = tn
        self.port_indexes = params.get('port_indexes')

    def run_command(self, protocol):
        self.tn.write("line\r\n".encode('utf-8'))
        for port in self.port_indexes:
            self.tn.write("closeport\r\n".encode('utf-8'))
            self.tn.write("0-{0}\r\n".format(port['slot_number']).encode('utf-8'))
            time.sleep(1)
            self.tn.write("{0}\r\n".format(port['port_number']).encode('utf-8'))
            time.sleep(1)

            self.tn.write("openportselt\r\n".encode('utf-8'))
            self.tn.write("0-{0}\r\n".format(port['slot_number']).encode('utf-8'))
            time.sleep(1)
            self.tn.write("{0}\r\n".format(port['port_number']).encode('utf-8'))
            time.sleep(1)
            self.tn.write("1\r\n".encode('utf-8'))
            time.sleep(1)

            self.tn.write("openport\r\n".encode('utf-8'))
            self.tn.write("0-{0}\r\n".format(port['slot_number']).encode('utf-8'))
            time.sleep(1)
            self.tn.write("{0}\r\n".format(port['port_number']).encode('utf-8'))
            time.sleep(1)

        result = {"result": "Port is being SELT status."}
        print '==================================='
        print result
        print '==================================='
        if protocol == 'http':
            return result
        elif protocol == 'socket':
            self.fiberhomeAN2200_q.put((
                "update_dslamport_command_result",
                self.dslam_id,
                self.port_indexes,
                "port disable",
                result))
