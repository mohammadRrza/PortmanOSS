import telnetlib
import time
from base_command import BaseCommand
class DeleteProfile(BaseCommand):
    __slot__ = ('tn', 'profile', 'dslam_id', 'fiberhomeAN2200_q')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.fiberhomeAN2200_q = fiberhomeAN2200_q
        self.dslam_id = params.get('dslam_id')
        self.profile = params.get('profile')

    def run_command(self, protocol):
        self.tn.write("line\r\n".encode('utf-8'))
        self.tn.write("deleteprf\r\n".encode('utf-8'))

        # search on AD32+ type
        self.tn.write("5\r\n".encode('utf-8'))
        self.tn.write("end\r\n".encode('utf-8'))
        result = self.tn.read_until('end')
        lstProfile = re.findall(r'\s(\S*\.prf)',result)
        delete_profile_index = None
        for index, line in enumerate(lstProfile, 1):
            if self.profile == line:
                delete_profile_index = index
                break
        if not delete_profile_index:
            # search on AD32 type
            self.tn.write("exit\r\n".encode('utf-8'))
            self.tn.write("deleteprf\r\n".encode('utf-8'))
            self.tn.write("2\r\n".encode('utf-8'))
            self.tn.write("end\r\n".encode('utf-8'))
            result = self.tn.read_until('end')
            print result
            lstProfile = re.findall(r'\s(\S*\.prf)',result)
            for index, line in enumerate(lstProfile, 1):
                print line
                if self.profile == line:
                    delete_profile_index = index
                    break
        if not delete_profile_index:
            print {"result": "{0} profile doesn't exist.".format(self.profile)}
            return {"result": "{0} profile doesn't exist.".format(self.profile)}

        self.tn.write("{0}\r\n".format(delete_profile_index).encode('utf-8'))
        time.sleep(1)
        self.tn.write("Y\r\n".encode('utf-8'))
        result = {"result": "profile {0} was deleted.".format(self.profile)}

        print '**********************************'
        print result
        print '**********************************'
        if protocol == 'http':
            return result
        elif protcol == 'socket':
            self.fiberhomeAN2200_q.put((
                "update_dslam_command_result",
                self.dslam_id,
                "profile adsl delete",
                result))

