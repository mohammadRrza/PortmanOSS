import telnetlib

class DeleteProfile(object):
    __slot__ = ('tn', 'profile', )
    def __init__(self, params=None):
        self.tn = tn
        self.profile = params['profile']

    def run_command(self):
        self.tn.write("profile adsl delete {0}\r\n\r\n".format(self.__profile).encode('utf-8'))
        print '***********************************************'
        print "{0} profile adsl deleted".format(self.profile)
        print '***********************************************'
        return {"result": "{0} profile adsl deleted".format(self.profile)}
