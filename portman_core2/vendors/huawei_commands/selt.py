import telnetlib
import sys
import time
from command_base import BaseCommand
import re

class Selt(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__port_indexes = params['port_indexes']

    @property
    def HOST(self):
        return self.__HOST

    @HOST.setter
    def HOST(self, value):
        self.__HOST = value

    @property
    def telnet_username(self):
        return self.__telnet_username

    @telnet_username.setter
    def telnet_username(self, value):
        self.__telnet_username = value

    @property
    def telnet_password(self):
        return self.__telnet_password

    @telnet_password.setter
    def telnet_password(self, value):
        self.__telnet_password = value

    def __clear_port_name(self,port_name):
        pattern = r'\d+(\s)?-(\s)?\d+'
        st = re.search(pattern,port_name,re.M|re.DOTALL)
        return st.group()

    retry = 1
    def run_command(self):
        output = ""
        results = []
        try:
            prompt = 'command'
            c_n = 1
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\n").encode('utf-8'))
            tn.write((self.__telnet_password + "\n").encode('utf-8'))
            for port_item in self.__port_indexes:
                tn.write("diagnostic selt test {0}-{1}\n".format(port_item['slot_number'], port_item['port_number']).encode('utf-8'))
                time.sleep(1)
            tn.write(prompt+str(c_n)+"\n")
            tn.read_until(prompt+str(c_n))
            c_n += 1
            time.sleep(10)
            for port_item in self.__port_indexes:
                tn.write("diagnostic selt show {0}-{1}\n".format(port_item['slot_number'], port_item['port_number']).encode('utf-8'))
                tn.write(prompt+str(c_n)+"\n")
                output = tn.read_until(prompt+str(c_n)).split('\n')[-2]
                while 'INPROGRESS' in output:
                    c_n += 1
                    tn.write('diagnostic selt show {0}-{1}\n'.format(port_item['slot_number'], port_item['port_number']).encode('utf-8'))
                    tn.write(prompt+str(c_n)+'\n')
                    output = tn.read_until(prompt+str(c_n)).split('\n')[-2]
                    time.sleep(10)
                output = output.replace(self.__clear_port_name(output),'')
                result_values = output.split()
                results.append(dict(port={'card': port_item['slot_number'],'port': port_item['port_number']}, inprogress=result_values[0]\
                    ,cableType=result_values[1], loopEstimateLength=' '.join(result_values[2:])))
            tn.write('exit\r\n')
            tn.write("y\r\n")
            tn.close()
            print '**********************************'
            print {'result': results}
            print '**********************************'
            return results
        except Exception,e:
            print e
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
            else:
                return dict(port_indexes=self.__port_indexes, inprogress='Connection Error'\
                        ,cableType=None, loopEstimateLength=None, result='selt command on ports give error')
