import telnetlib
import time
from socket import error as socket_error
import re
from .base_command import BaseCommand

class ShowShelf(BaseCommand):
    __slot__ = ('tn', 'dslam_id', 'fiberhomeAN5006_q')
    def __init__(self, tn, params, fiberhomeAN5006_q=None):
        self.tn = tn
        self.dslam_id = params.get('dslam_id')
        self.fiberhomeAN5006_q = fiberhomeAN5006_q

    def run_command(self, protocol):
        self.tn.write(("cd device\r\n").encode('utf-8'))
        self.tn.read_until("#")
        self.tn.write(("show card status\r\n").encode('utf-8'))
        result = '\n'.join(self.tn.read_until("#").split('\n')[:-1])
        self.tn.write("exit\r\n")

        results = {'result': result}
        print('===================================')
        print(results)
        print('===================================')

        if protocol == 'http':
            return results
        elif protocol == 'socket':
            self.fiberhomeAN5006_q.put(("update_dslam_command_result",
                self.dslam_id,
                "show shelf",
                results))

