import telnetlib
import time

class CreateProfile(object):
    __slot__ = ('tn', 'profile', 'us_max_rate', 'ds_max_rate')
    def __init__(self, tn, params=None):
        self.tn = tn
        self.profile = params['profile']
        self.us_max_rate = params['us-max-rate']
        self.ds_max_rate = params['ds-max-rate']

    def run_command(self):
        self.tn.write("profile adsl set {0} {1} {2}\r\n\r\n".format(
            self.profile,
            self.us_max_rate,
            self.ds_max_rate
        ).encode('utf-8'))
        time.sleep(1)
        self.tn.write("end\r\n")
        result = self.tn.read_until('end')
        print '*******************************************'
        print "{0} profile created".format(self.profile)
        print '*******************************************'
        return {"result": "{0} profile created".format(self.profile)}
