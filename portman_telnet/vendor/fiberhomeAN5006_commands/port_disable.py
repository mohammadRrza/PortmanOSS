import telnetlib
import time
import re
from .base_command import BaseCommand

class PortDisable(BaseCommand):
    __slot__ = ('tn', 'port_indexes', 'dslam_id', 'fiberhomeAN5006_q')
    def __init__(self, tn, params, fiberhomeAN5006_q=None):
        self.tn = tn
        self.dslam_id = params.get('dslam_id')
        self.port_indexes = params.get('port_indexes')
        self.fiberhomeAN5006_q = fiberhomeAN5006_q

    def run_command(self, protocol):
        self.tn.write(("cd service\r\n").encode('utf-8'))
        self.tn.read_until("#")
        output = []
        for port in self.port_indexes:
            self.tn.write("set interface {0}/{1} disable\r\n".format(port.get('slot_number'), port.get('port_number')).encode('utf-8'))
            self.tn.read_until("#")
            output.append('port {0}-{1} disabled'.format(port.get('slot_number'), port.get('port_number')))
        self.tn.write("exit\r\n")

        results = {"result": '\n'.join(output)}
        print('===================================')
        print(results)
        print('===================================')

        if protocol == 'http':
            return results
        elif protocol == 'socket':
            self.fiberhomeAN5006_q.put(("update_dslamport_command_result",
                self.dslam_id,
                self.port_indexes,
                "port disable",
                results))
