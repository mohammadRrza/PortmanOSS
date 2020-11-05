import telnetlib
import time
from base_command import BaseCommand

class ChangeProfile(BaseCommand):
    __slot__ = ('tn', 'port_indexes', 'new_profile')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.dslam_id = params.get('dslam_id')
        self.port_indexes = params.get('port_indexes')
        self.new_profile = params.get('new_lineprofile')
        self.fiberhomeAN2200_q = fiberhomeAN2200_q

    def run_command(self, protocol):
        self.tn.write("line\r\n".encode('utf-8'))
        # search on AD32+ type
        for port in self.port_indexes:
            self.tn.write("cfgport\r\n".encode('utf-8'))
            self.tn.write("0-{0}\r\n".format(port['slot_number']).encode('utf-8'))
            time.sleep(1)
            self.tn.write("{0}\r\n".format(port['port_number']).encode('utf-8'))
            time.sleep(1)
            self.tn.write(("end\r\n").encode('utf-8'))
            data = self.tn.read_until('end')
            profiles = re.findall(r'\)(\S*\.prf)',data)
            for index, profile in enumerate(profiles):
                if self.new_profile == profile:
                    self.tn.write("{0}\r\n".format(index).encode('utf-8'))
            time.sleep(1)
        result = {"result": "ports profile are changed to {0}".format(self.new_profile)}

        print '==================================='
        print result
        print '==================================='
        if protocl == 'http':
            return result
        elif protocl == 'socket':
            self.fiberhomeAN2200_q.put(("update_dslamport_command_result",
                self.dslam_id,
                self.port_indexes,
                "profile adsl change",
                result))
            self.fiberhomeAN2200_q.put((
                    "change_port_line_profile",
                    self.dslam_id,
                    self.port_indexes,
                    self.new_profile
                ))
