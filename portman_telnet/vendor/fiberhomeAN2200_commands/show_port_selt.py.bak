import telnetlib
import time
from base_command import BaseCommand

class ShowPortSelt(BaseCommand):
    __slot__ = ('tn', 'port_indexes', 'fiberhomeAN2200_q', 'dslam_id')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.dslam_id = params.get('dslam_id')
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.tn = tn
        self.port_indexes = params.get('port_indexes')

    def run_command(self, protocol):
        self.tn.write("line\r\n".encode('utf-8'))
        self.tn.read_until('>', 5)
        ports = []
        for port in self.port_indexes:
            self.tn.write("showportselt\r\n".encode('utf-8'))
            self.tn.read_until('>', 5)
            self.tn.write("0-{0}\r\n".format(port['slot_number']).encode('utf-8'))
            time.sleep(1)
            self.tn.write("{0}\r\n".format(port['port_number']).encode('utf-8'))
            time.sleep(1)
            self.tn.write("1\r\n".encode('utf-8'))
            time.sleep(1)
            data = self.tn.read_until('>', 5)
            selt_result = {
                    'slot_number': port['slot_number'],
                    'port_number': port['port_number']
                    }
            if 'in SELT_APP mode!' in data:
                selt_result['loopEstimateLength'] = 'Port is in SELT_APP mode!'

            elif 'not in SELT mode!' in data:
                selt_result['loopEstimateLength'] = 'Port is not in SELT mode!'
            else:
                selt_result['loopEstimateLength'] = int(re.search(r'\s+Line\slength\s+:\s+(\d+)\sInch', st).groups()[0]) / 39.37007874015748

            ports.append(selt_result)

        result = {"result": ports}
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
