import telnetlib
import time
from base_command import BaseCommand

class ShowHostname(BaseCommand):
    __slot__ = ('tn', 'dslam_id', 'fiberhomeAN2200_q')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.dslam_id = params.get('dslam_id')
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.slot_number = params.get('slot_number')

    def run_command(self, protocol):
        data = self.tn.read_until('>', 5)
        hostname = data.split('>')[0]
        result = {"result": hostname}

        print '==================================='
        print result
        print '==================================='

        if protocol == 'http':
            return result
        elif protocl == 'socket':
            self.fiberhomeAN2200_q.put((
                "update_dslam_command_result",
                self.dslam_id,
                "lcman reset slot",
                result
                ))
