import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class GetDSLAMBoard(BaseCommand):
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

    retry = 1

    def run_command(self):
        try:
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            time.sleep(1)
            tn.read_until(b'Password:')
            tn.write(b"lcman show\r\n")
            time.sleep(1)
            tn.write(b"end\r\n")
            result = tn.read_until(b"end")
            lines = result.split(b'\r\n')
            lines = lines[6:len(lines) - 2]
            boards = []
            for line in lines:
                card_number = status = hw_version = temperature = card_type = uptime = fw_version = serial_number = mac_address = inband_mac_address = outband_mac_address = None
                items = line.split()
                card_number, status = items[0:2]
                if status == '-':
                    status = 'deactive'.format(card_number)
                else:
                    card_type, uptime, fw_version = items[2:5]
                    uptime = '{0} days, {1}:{2}:{3}'.format(*uptime.split(':'))
                    time.sleep(2)
                    tn.write("lcman show {0}\r\n".format(card_number).encode('utf-8'))
                    time.sleep(2)
                    tn.write("end{0}\r\n".format(card_number).encode('utf-8'))
                    result = tn.read_until("end{0}".format(card_number).encode('utf-8'))
                    try:
                        serial_number = \
                            re.search(r'hardware serial number:\s(?:\w+)?', result, re.M).group(0).split(':')[1].strip()
                        temperature = [{'name': temp.split(':')[0].strip(), 'value': temp.split(':')[1].strip()} for
                                       temp in re.findall(r'Temp\d+:\s\d+\.\d+', result, re.M)]
                        hw_version = re.search(r'hardware version(\s)*:(\s)*\w+', result, re.M).group(0).split()[-1]
                        try:
                            mac_address = \
                                re.search(r'mac address(\s)+:\s(?:[0-9a-fA-F]:?){12}', result, re.M).group(0).split()[3]
                        except:
                            inband_mac_address = \
                                re.search(r'inband\smac(\s)+:\s([0-9A-F]{2}[:-]){5}([0-9A-F]{2})', result, re.M).group(
                                    0).split()[3]
                            outband_mac_address = \
                                re.search(r'outband\smac(\s)+:\s([0-9A-F]{2}[:-]){5}([0-9A-F]{2})', result, re.M).group(
                                    0).split()[3]
                    except Exception as ex:
                        print(ex)
                        print(result)
                        continue
                boards.append(dict(
                    card_number=card_number,
                    status=status,
                    card_type=card_type,
                    uptime=uptime,
                    fw_version=fw_version,
                    serial_number=serial_number,
                    temperature=temperature,
                    hw_version=hw_version,
                    mac_address=mac_address,
                    inband_mac_address=inband_mac_address,
                    outband_mac_address=outband_mac_address))
            tn.write(b"exit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            return {"result": boards}
        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
        except Exception as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
