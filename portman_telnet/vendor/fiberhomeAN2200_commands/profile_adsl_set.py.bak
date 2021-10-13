import telnetlib
import time
import re
from base_command import BaseCommand

class ProfileADSLSet(BaseCommand):
    __slot__ = ('tn', 'fiberhomeAN2200_q', 'dslam_id')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.params = params
        self.dslam_id = params.get('dslam_id')
        self.profile = params.get('profile')

    def run_command(self, protocol):
        profiles = []
        self.tn.write("line\r\n".encode('utf-8'))
        self.tn.write("showprf\r\n".encode('utf-8'))
        self.tn.read_until('>')
        # search on AD32+ type
        self.tn.write("5\r\n".encode('utf-8'))
        time.sleep(1)
        self.tn.read_until('exit')
        result = self.tn.read_until('exit')
        com = re.compile(r'\s+\(\s?(?P<id>\d+)\)\s+(?P<name>\S)+\s')
        profiles_objects = [m.groupdict() for m in com.finditer(st)]
        profiles_dict = [{item['name']: item['id']} for item in profiles_objects]
        if self.profile in profile_dict.keys():
            profile_id = profile_dict[self.profile]
        for port in self.port_indexes:
            self.tn.write("cfgport\r\n".encode('utf-8'))
            self.tn.write("0-{0}\r\n".format(port.get('slot_number')).encode('utf-8'))
            self.tn.write("{0}\r\n".format(port.get('port_number')).encode('utf-8'))
            time.sleep(1)
        '''
        else:
        # search on AD32 type
        self.tn.write("showprf\r\n".encode('utf-8'))
        self.tn.read_until('>')
        self.tn.write("2\r\n".encode('utf-8'))
        time.sleep(1)
        self.tn.write("exit\r\n".encode('utf-8'))
        result = self.tn.read_until('exit')
        com = re.compile(r'\s+\(\s?(?P<id>\d+)\)\s+(?P<name>\S)+\s')
        profiles_objects = [m.groupdict() for m in com.finditer(st)]
        profiles_dict = [{item['name']: item['id']} for item in profiles_objects]
        if self.profile in profile_dict.keys():
            profile_id = profile_dict[self.profile]
        '''


        result = {"result": 'profile adsl set is ok!'}

        print '**********************************'
        print result
        print '**********************************'
        if protocol == 'socket':
            self.__django_orm_queue.put(("add_line_profile",
                self.params,
            ))
        elif protocol == 'http':
            return result

