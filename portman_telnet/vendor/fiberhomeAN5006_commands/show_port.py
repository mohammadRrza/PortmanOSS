import telnetlib
import time
from socket import error as socket_error
import re
from .base_command import BaseCommand


class ShowPort(BaseCommand):
    __slot__ = ('tn', 'dslam_id', 'fiberhomeAN5006_q', 'port_indexes')
    def __init__(self, tn, params, fiberhomeAN5006_q=None):
        self.tn = tn
        self.dslam_id = params.get('dslam_id')
        self.fiberhomeAN5006_q = fiberhomeAN5006_q
        self.port_indexes = params.get('port_indexes')

    def run_command(self, protocol):
        self.tn.write(("cd service\r\n").encode('utf-8'))
        self.tn.read_until("#")
        data = []
        for port in self.port_indexes:
            self.tn.write("telnet slot {0}\r\n".format(port.get('slot_number')).encode('utf-8'))
            self.tn.read_until("#")
            self.tn.write("cd dsp\r\n".format(1).encode('utf-8'))
            self.tn.read_until("#")
            self.tn.write("show port status {0}\r\n".format(port.get('port_number')).encode('utf-8'))
            output = '\n'.join(self.tn.read_until("#").split('\n')[:-1])
            self.tn.write("exit\r\n")
            self.tn.write("exit\r\n")
            data.append(output)
        self.tn.write("exit\r\n")
        data  ='\n'.join(data)

        results = {'result': data}
        print('===================================')
        print(results)
        print('===================================')

        if protocol == 'http':
            return results
        elif protocol == 'socket':
            self.fiberhomeAN5006_q.put(("update_dslam_command_result",
                self.dslam_id,
                "show port",
                results))
