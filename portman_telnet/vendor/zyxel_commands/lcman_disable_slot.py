import telnetlib

class LcmanDisableSlot(object):
    __slot__ = ('tn', 'slot')
    def __init__(self, tn, params):
        self.tn = tn
        self.slot = params['slot']

    def run_command(self):
        self.tn.write("lcman disable {0}\r\n\r\n".format(self.__slot).encode('utf-8'))
        print '*************************************'
        print "disable slot {0}".format(self.slot)
        print '*************************************'
        return "disable slot {0}".format(self.slot)
