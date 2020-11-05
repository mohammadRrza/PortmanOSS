import telnetlib
import time
import re

from base_command import BaseCommand

class GetPortsVpiVci(BaseCommand):
    __slot__ = ('tn', 'dslam_id')
    def __init__(self, tn, params, queue):
        self.tn = tn
        self.queue = queue
        self.dslam_id = params.get('dslam_id')

    def run_command(self):
        print '------------------------------'
        print self.dslam_id
        print '------------------------------'
        self.tn.write("core\r\n".encode('utf-8'))
        # search on AD32+ type
        self.tn.write("showallvc\r\n".encode('utf-8'))
        time.sleep(1)
        self.tn.write("C\r\n".encode('utf-8'))
        time.sleep(20)
        self.tn.write("end_of_line\r\n".encode('utf-8'))
        data = self.tn.read_until('end_of_line', 5)
        com = re.compile(r'\d+\s+\S+\s+\d+\-(?P<slot_number>\d+)-\s?(?P<port_number>\d+)\s+(?P<vpi>\d+)/\s?(?P<vci>\d+)')
        results = [m.groupdict() for m in com.finditer(data)]
        for item in results:
            item['port_index'] = item['slot_number'] + item['port_number']
        print '-----------------------------------'
        print results
        print '-----------------------------------'

        self.queue.put(('update_port_vpi_vci', self.dslam_id, results))
