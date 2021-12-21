import os
import telnetlib
import sys
import time
from socket import error as socket_error
import re
from .command_base import BaseCommand
#from easysnmp import Session

class ProfileADSLShow(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.device_ip = params.get('device_ip')

    @property
    def HOST(self):
        return self.__HOST

    @HOST.setter
    def HOST(self, value):
        self.__HOST = value

    @property
    def port_name(self):
        return self.__port_name

    @port_name.setter
    def port_name(self, value):
        self.__port_name = self.__clear_port_name(value)

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
        try:
            tn = telnetlib.Telnet(self.__HOST, timeout=10)
            tn.write((self.__telnet_username + "\n").encode('utf-8'))
            tn.read_until(b"Password:")
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            err1 = tn.read_until(b'Communications Corp.', 2)
            if "Password:" in str(err1):
                return "Telnet Username or Password is wrong! Please contact with core-access department."
            tn.write(("profile adsl show\r\n").encode('utf-8'))
            time.sleep(0.5)
            # tn.read_until("profile adsl show")
            # lstresult=[]
            # for item in range(7):
            #     tn.write("n\r\n")
            # tn.write("next\r\n")
            # result = tn.read_until("# n")
            # result = re.findall(r'\d+\.\s(\S*)',result)
            tn.write(b"n\r\n")
            tn.write(b"end")
            result = tn.read_until(b"end")
            if self.device_ip == '127.0.0.1' or self.device_ip == '172.28.238.114':
                return dict(result=result.decode('utf-8'), status=200)
            result = str(result).split("\\r\\n")
            result = [re.sub(r'\d+[.]\s', '', val) for val in result if re.search(r'\d+[.]\s', val)]
            return dict(result=result, status=200)

            lstProfile = re.findall(r'\d+\.\s(\S*)',result)
            for profilename in lstProfile:
                tn.write(("profile adsl show {0}\r\n".format(profilename)).encode('utf-8'))
                tn.read_until("adsl profile: ")
                tn.write('end\r\n')
                st = tn.read_until("end")
                channel_mode = None
                template_type = 'adsl2+'
                max_us_transmit_rate, max_ds_transmit_rate = re.search(r'\s+max\srate\s+\(Kbps\):\s+(\d+)\s+(\d+)\s+', st, re.M).groups()
                min_us_transmit_rate, min_ds_transmit_rate = re.search(r'\s+min\srate\s+\(Kbps\):\s+(\d+)\s+(\d+)\s+', st, re.M).groups()
                max_us_interleaved, max_ds_interleaved = re.search(r'\s+latency\sdelay\s+\(ms\):\s+(\d+|fast)\s+(\d+|fast)\s+', st, re.M).groups()
                if max_us_interleaved == 'fast':
                    channel_mode = 'fast'
                else:
                    channel_mode = 'interleaved'
                max_us_snr_margin, max_ds_snr_margin = re.search(r'\s+max\smargin\s+\(dB\):\s+(\d+\.\d+)\s+(\d+\.\d+)\s+',st, re.M).groups()
                min_us_snr_margin, min_ds_snr_margin = re.search(r'\s+min\smargin\s+\(dB\):\s+(\d+\.\d+)\s+(\d+\.\d+)\s+',st, re.M).groups()
                us_snr_margin, ds_snr_margin = re.search(r'\s+target\smargin\s+\(dB\):\s+(\d+\.\d+)\s+(\d+\.\d+)\s+',st, re.M).groups()
                transmit_rate_adaptation = re.search(r'\s+sra\smode\s+:\s+(\S+)\s+(\S+)\s+',st, re.M).groups()
                usra_us_mgn, dsra_us_mgn = re.search(r'\s+up\sshift\smgn\s+\(dB\):\s+(\d+\.\d+)\s+(\d+\.\d+)\s+',st, re.M).groups()
                usra_ds_mgn, dsra_ds_mgn = re.search(r'\s+down\sshift\smgn\s+\(dB\):\s+(\d+\.\d+)\s+(\d+\.\d+)\s+',st, re.M).groups()
                lstresult.append({
                    'name': profilename,
                    'channel_mode': channel_mode,
                    'template_type': template_type,
                    'max_us_transmit_rate': max_us_transmit_rate,
                    'max_ds_transmit_rate': max_ds_transmit_rate,
                    'min_us_transmit_rate': min_us_transmit_rate,
                    'min_ds_transmit_rate': min_ds_transmit_rate,
                    'max_us_interleaved': max_us_interleaved,
                    'max_ds_interleaved': max_ds_interleaved,
                    'us_snr_margin': us_snr_margin,
                    'ds_snr_margin': ds_snr_margin,
                    'extra_settings':{
                        'usra': transmit_rate_adaptation[0],
                        'usra_us_mgn': usra_us_mgn,
                        'dsra_ds_mgn': dsra_ds_mgn,
                        'dsra_us_mgn': dsra_us_mgn,
                        'usra_ds_mgn': usra_ds_mgn,
                        'dsra': transmit_rate_adaptation[1],
                        'max_ds_snr_margin': max_ds_snr_margin,
                        'min_us_snr_margin': min_us_snr_margin,
                        'max_us_snr_margin': max_us_snr_margin,
                        'min_ds_snr_margin': min_ds_snr_margin,
                        },
                    })

            """print '++++++++++++++++++++++++'
            print lstresult
            print '++++++++++++++++++++++++'
            """
            tn.write("exit\r\n")
            tn.write("y\r\n")
            tn.close()
            return {"result": lstresult}
        # except Exception as ex:
        #     print('????????????????????????????')
        #     print((self.__HOST, self.__telnet_username, self.__telnet_password))
        #     print(ex)
        #     print('????????????????????????????')
        #     return self.run_command()
        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 3:
                return self.run_command()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print((str(exc_tb.tb_lineno)))
            print(e)
            self.retry += 1
            if self.retry < 3:
                return self.run_command()
