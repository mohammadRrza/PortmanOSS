import telnetlib
import sys
import time
from socket import error as socket_error
import re
from command_base import BaseCommand
#from easysnmp import Session

class ProfileADSLShow(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__params = params

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
            tn = telnetlib.Telnet(self.__HOST)
            if tn.read_until('>>User name:'):
                tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            if tn.read_until('>>User password:'):
                tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            tn.write("\r\n")
            tn.write("\r\n")
            tn.write("enable\r\n".encode('utf-8'))
            tn.write("config\r\n".encode('utf-8'))
            tn.write("display adsl line-profile\r\n".encode('utf-8'))
            time.sleep(1)
            tn.write("\r\n")
            time.sleep(1)
            tn.write("n\r\n")
            time.sleep(1)
            tn.write("end\r\n")
            result = tn.read_until("end")
            profiles = re.findall(r'\s+(\d+)\s(\S+)\s+\S+\s?\S+?\s+\S+\s+\d+\s+\d+\s+\d+\s+\d+', result)
            profile_list = []
            for profile_index, profile_name in profiles:
                time.sleep(1)
                profile = {'index': profile_index, 'name': profile_name}
                tn.write("display adsl line-profile {0}\r\n".format(profile_index).encode('utf-8'))
                tn.write("\r\n")
                time.sleep(1)
                tn.write("n\r\n")
                time.sleep(1)
                tn.write("end\r\n")
                result = tn.read_until("end")
                profile['template_type'] = "adsl2+"
                profile['channel_mode'] = re.search(r'\s+Channel\smode\s+:\s(\S+)', result).groups()[0]
                if profile['channel_mode'] != 'Fast':
                    profile['max_ds_interleaved'] = re.search(r'\s+Maximum\sdownstream\sinterleaved\sdelay\(ms\)\s+:\s(\S+)', result).groups()[0]
                    profile['max_us_interleaved'] = re.search(r'\s+Maximum\supstream\sinterleaved\sdelay\(ms\)\s+:\s(\S+)', result).groups()[0]
                profile['ds_snr_margin'] = re.search(r'\s+Target\sdownstream\sSNR\smargin\(dB\)\s+:\s(\S+)', result).groups()[0]
                profile['us_snr_margin'] = re.search(r'\s+Target\supstream\sSNR\smargin\(dB\)\s+:\s(\S+)', result).groups()[0]
                profile['min_ds_transmit_rate'] = re.search(r'\s+Minimum\stransmit\srate\sdownstream\(Kbps\)\s+:\s(\S+)', result).groups()[0]
                profile['max_ds_transmit_rate'] = re.search(r'\s+Maximum\stransmit\srate\sdownstream\(Kbps\)\s+:\s(\S+)', result).groups()[0]
                profile['min_us_transmit_rate'] = re.search(r'\s+Minimum\stransmit\srate\supstream\(Kbps\)\s+:\s(\S+)', result).groups()[0]
                profile['max_us_transmit_rate'] = re.search(r'\s+Maximum\stransmit\srate\supstream\(Kbps\)\s+:\s(\S+)', result).groups()[0]

                #extra section
                profile_extra_settings = {}
                profile_extra_settings['usra'] = re.search(r'\s+Downstream\sform\sof\stransmit\srate\sadaptation\s+:\s(\S+)', result).groups()[0]
                profile_extra_settings['dsra'] = profile_extra_settings['usra']
                profile_extra_settings['min_us_snr_margin'] = re.search(r'\s+Minimum\sacceptable\supstream\sSNR\smargin\(dB\)\s+:\s(\S+)', result).groups()[0]
                profile_extra_settings['max_us_snr_margin'] = re.search(r'\s+Maximum\sacceptable\supstream\sSNR\smargin\(dB\)\s+:\s(\S+)', result).groups()[0]
                profile_extra_settings['min_ds_snr_margin'] = re.search(r'\s+Minimum\sacceptable\sdownstream\sSNR\smargin\(dB\)\s+:\s(\S+)', result).groups()[0]
                profile_extra_settings['max_ds_snr_margin'] = re.search(r'\s+Maximum\sacceptable\sdownstream\sSNR\smargin\(dB\)\s+:\s(\S+)', result).groups()[0]
                profile_extra_settings['dsra_ds_mgn'] = re.search(r'\s+Downstream\sSNR\smargin\sfor\srate\sdownshift\(dB\)\s+:\s(\S+)', result).groups()[0]
                profile_extra_settings['dsra_us_mgn'] = re.search(r'\s+Upstream\sSNR\smargin\sfor\srate\sdownshift\(dB\)\s+:\s(\S+)', result).groups()[0]
                profile_extra_settings['usra_ds_mgn'] = re.search(r'\s+Downstream\sSNR\smargin\sfor\srate\supshift\(dB\)\s+:\s(\S+)', result).groups()[0]
                profile_extra_settings['usra_us_mgn'] = re.search(r'\s+Upstream\sSNR\smargin\sfor\srate\supshift\(dB\)\s+:\s(\S+)', result).groups()[0]

                profile['extra_settings'] = profile_extra_settings
                profile_list.append(profile)
            tn.write("quit\r\n")
            tn.write("y\r\n")
            tn.close()
            print '----------------------------'
            print profile_list
            print '----------------------------'
            return {"result": profile_list}
        except (EOFError,socket_error) as e:
            print e
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
        except Exception,e:
            print e
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
