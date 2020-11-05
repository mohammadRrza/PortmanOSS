import telnetlib
import re
import time
from .base_command import BaseCommand

class PortEnable(BaseCommand):
    __slot__ = ('tn', 'fiberhomeAN3300_q', 'dslam_id', 'port_indexes')
    def __init__(self, tn, params, fiberhomeAN3300_q=None):
        self.tn = tn
        self.fiberhomeAN3300_q = fiberhomeAN3300_q
        self.dslam_id = params.get('dslam_id')
        self.port_indexes = params.get('port_indexes')

    def run_command(self, protocol):
        self.tn.write("cd device\r\n".encode('utf-8'))
        self.tn.read_until('>',5)
        for port in self.port_indexes:
            self.tn.write("set xdsl port {0}:{1} enable\r\n".format().encode('utf-8'))

        result = {'result': 'ports are enabled'}

        if protocol == 'http':
            return result
        elif protocol == 'socket':
            self.fiberhomeAN3300_q.put((
                "update_dslamport_command_result",
                self.dslam_id,
                self.port_indexes,
                "port enable",
                result))

