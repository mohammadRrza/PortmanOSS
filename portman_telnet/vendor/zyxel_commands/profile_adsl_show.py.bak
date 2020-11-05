import telnetlib
import time

class ProfileADSLShow(object):
    __slot__ = ('tn', )
    def __init__(self, tn, params=None):
       self.tn = tn

    def run_command(self):
        self.tn.write(("profile adsl show\r\n").encode('utf-8'))
        self.tn.read_until("profile adsl show")
        lstresult=[]
        for item in range(7):
            time.sleep(1)
            self.tn.write("n\r\n")
            self.tn.write("next\r\n")
            result = self.tn.read_until("next")
            if 'next' in result:
                break
        lstProfile=re.findall(r'\d+\.\s\S*',result)
        for item in lstProfile:
            lstresult.append(item.split(' ')[-1].strip())
        print '***********************************'
        print {"result": lstresult}
        print '***********************************'
        return {"result": lstresult}
