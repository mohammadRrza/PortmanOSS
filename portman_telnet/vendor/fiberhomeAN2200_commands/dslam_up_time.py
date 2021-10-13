import telnetlib
import time
from .base_command import BaseCommand

class DSLAMUpTime(BaseCommand):
    __slot__ = ('tn', 'dslam_id', 'fiberhomeAN2200_q')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.dslam_id = params.get('dslam_id')
        self.fiberhomeAN2200_q = fiberhomeAN2200_q

    def run_command(self, protocol):
        self.tn.write("showtime\r\n".encode('utf-8'))
        data = self.tn.read_until('>', 5)
        if 'timeout' in data.lower():
            self.tn.close()
            raise ValueError('first please login session')

        data = self.tn.read_until('>')
        result = {"result": data.split('\n')[-2]}

        print('===================================')
        print(result)
        print('===================================')

        if protocol == 'http':
            return result
        elif protocl == 'socket':
            self.fiberhomeAN2200_q.put((
                "update_dslam_command_result",
                self.dslam_id,
                "show time",
                result
                ))
