import telnetlib
import time
import re
from .base_command import BaseCommand

class ProfileADSLShow(BaseCommand):
    __slot__ = ('tn', 'fiberhomeAN2200_q', 'dslam_id')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.dslam_id = params.get('dslam_id')

    def run_command(self, protocol):
        profiles = []
        self.tn.write("line\r\n".encode('utf-8'))
        self.tn.write("showprf\r\n".encode('utf-8'))
        # search on AD32+ type
        self.tn.write("5\r\n".encode('utf-8'))
        time.sleep(1)
        self.tn.write("end\r\n".encode('utf-8'))
        result = self.tn.read_until('end')
        max_number = re.search(r'\(\s?(\d+)\)\s','\n'.join(result.split('\n')[-1::-1])).groups()[0]
        self.tn.write("0~{0}\r\n".format(max_number).encode('utf-8'))
        time.sleep(2)
        self.tn.write("end\r\n".encode('utf-8'))
        profiles_data = self.tn.read_until('end').split('ADSL  PROFILE :')
        self.__find_profile_data(profiles, profiles_data)

        # search on AD32 type
        self.tn.write("showprf\r\n".encode('utf-8'))
        self.tn.write("2\r\n".encode('utf-8'))
        time.sleep(1)
        self.tn.write("end\r\n".encode('utf-8'))
        result = self.tn.read_until('end')
        max_number = re.search(r'\(\s?(\d+)\)\s','\n'.join(result.split('\n')[-1::-1])).groups()[0]
        self.tn.write("0~{0}\r\n".format(max_number).encode('utf-8'))
        time.sleep(2)
        self.tn.write("end\r\n".encode('utf-8'))
        profiles_data = self.tn.read_until('end').split('ADSL  PROFILE :')
        self.__find_profile_data(profiles, profiles_data)

        self.tn.write("exit\r\n".encode('utf-8'))
        result = {"result": profiles}

        #print '**********************************'
        #print result
        #print '**********************************'
        if protocol == 'socket':
            self.fiberhomeAN2200_q.put((
                "update_profile_adsl",
                profiles
                ))
        elif protocol == 'http':
            return result

    def __find_profile_data(self, profiles, profiles_data):
        for profile_data in profiles_data:
            try:
                rows = profile_data.split('\n')
                profile = {}
                profile['name'] = rows[0].strip()
                _, profile['channel_mode'] ,_ = [item for row in rows[4].split('|') for item in row.split()]

                if profile['channel_mode'] == 'Fast':
                    _, profile['us_snr_margin'], profile['min_us_transmit_rate'], profile['max_us_transmit_rate'] =\
                            [item for row in rows[8].split('|') for item in row.split()]
                    _, profile['ds_snr_margin'], profile['min_ds_transmit_rate'], profile['max_ds_transmit_rate'] =\
                            [item for row in rows[9].split('|') for item in row.split()]
                else:
                    _, profile['max_us_interleaved'], profile['us_snr_margin'], profile['min_us_transmit_rate'], profile['max_us_transmit_rate'] =\
                            [item for row in rows[8].split('|') for item in row.split()]
                    _, profile['max_ds_interleaved'], profile['ds_snr_margin'], profile['min_ds_transmit_rate'], profile['max_ds_transmit_rate'] =\
                            [item for row in rows[9].split('|') for item in row.split()]
                profiles.append(profile)
            except Exception as ex:
                print('=>>>>>>>>>>>>', ex)
                pass
