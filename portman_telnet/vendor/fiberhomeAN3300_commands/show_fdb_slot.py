import telnetlib
import re
import time
from .base_command import BaseCommand

class ShowFdbSlot(BaseCommand):
    __slot__ = ('tn', 'fiberhomeAN3300_q', 'dslam_id', 'slot_number')
    def __init__(self, tn, params, fiberhomeAN3300_q=None):
        self.tn = tn
        self.fiberhomeAN3300_q = fiberhomeAN3300_q
        self.dslam_id = params.get('dslam_id')
        self.slot_number = params.get('slot_number')

    def run_command(self, protocol):
        try:
            self.tn.write("cd fdb\r\n".encode('utf-8'))
            self.tn.read_until('>',5)
            self.tn.write("show fdb slot {0}\r\n".encode('utf-8'))
            data = self.tn.read_until('>',5)
            time.sleep(3)
            self.tn.write("n\r\n".encode('utf-8'))
            output = self.tn.read_until('>')
            com = re.compile(r'\s+(?P<mac>\S+)\s+(?P<slot>\d+)\:\s?(?P<port>\d+)\:\S+\s+(?P<vid>\S+)\s+\S+')
            results = [m.groupdict() for m in com.finditer(st)]
            result = {'result': results}

            if protocol == 'http':
                return result
            elif protocol == 'socket':
                self.fiberhomeAN3300_q.put((
                    "update_dslam_command_result",
                    self.dslam_id,
                    "show fdb slot",
                    result))

        except Exception as ex:
            print(ex)
            return {'result': 'error: show fdb slot command'}
