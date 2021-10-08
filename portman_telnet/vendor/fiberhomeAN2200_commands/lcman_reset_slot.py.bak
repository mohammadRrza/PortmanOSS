import telnetlib
import time
from base_command import BaseCommand

class LcmanResetSlot(BaseCommand):
    __slot__ = ('tn', 'dslam_id', 'fiberhomeAN2200_q', 'slot_number')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.dslam_id = params.get('dslam_id')
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.slot_number = params.get('slot_number')

    def run_command(self, protocol):
        self.tn.write("line\r\n".encode('utf-8'))
        data = self.tn.read_until('>', 5)
        if 'timeout' in data.lower():
            self.tn.close()
            raise ValueError('first please login session')
        self.tn.write("restartcard\r\n".encode('utf-8'))
        self.tn.read_until('>')
        time.sleep(1)
        self.tn.write("y\r\n".encode('utf-8'))
        self.tn.write("0-{0}\r\n".format(self.slot_number).encode('utf-8'))
        time.sleep(1)
        data = self.tn.read_until('>')
        result = {"result": data.split('\n')[-2]}

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
