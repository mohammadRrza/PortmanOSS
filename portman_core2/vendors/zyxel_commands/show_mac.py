import telnetlib
import time
from .command_base import BaseCommand
import re


class ShowMac(BaseCommand):
    def __init__(self, params):
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

    def __clear_port_name(self, port_name):
        pattern = r'\d+(\s)?-(\s)?\d+'
        st = re.search(pattern, port_name, re.M | re.DOTALL)
        return st.group()

    retry = 1

    def run_command(self):
        try:
            tn = telnetlib.Telnet(self.__HOST)
            time.sleep(1)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            if self.__telnet_password:
                tn.read_until(b"Password: ")
                tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            time.sleep(1)
            tn.write(b"show mac\r\nn")
            result = tn.read_until(b'show mac')
            if ">" in str(result):
                result = tn.read_until(b'>', 1)
                output = ''
                while '>' not in str(output):
                    output += result.decode()
                    result = tn.read_until(b'>', 1)
            else:
                result = tn.read_until(b'#', 1)
                output = ''
                while '#' not in str(output):
                    output += result.decode()
                    result = tn.read_until(b'#', 1)
            tn.write(b"exit\r\n")
            tn.write(b"y\r\n")
            tn.close()
            if self.device_ip == '127.0.0.1' or self.device_ip == '172.28.238.114':
                return dict(result=result.decode('utf-8'), status=200)
            result = str(output).split('\r\n')
            result = [val for val in result if re.search('--{4,}|:|Press', val)]
            for inx, line in enumerate(result):
                if "Press any key" in line:
                    del result[inx:inx + 3]
            return dict(result=result, status=200)
            lst_result = []
            com = re.compile(
                r"(?P<vlan_id>(\d))?(\s)*(?P<mac>([0-9A-F]{2}[:-]){5}([0-9A-F]{2}))(\s)*(?P<port>(\d+(\s)?-(\s)?\d+))$",
                re.MULTILINE | re.I)
            for line in results:
                try:
                    lst_result.append({
                        'vlan_id': com.search(line.strip()).group('vlan_id'),
                        'mac': com.search(line.strip()).group('mac'),
                        'port_number': com.search(line.strip()).group('port').split('-')[0].strip(),
                        'slot_number': com.search(line.strip()).group('port').split('-')[1].strip()
                    })
                except:
                    pass
            return {"result": lst_result}
        except Exception as e:
            print(('=>>>>>>>>>>>>', e))
            self.retry += 1
            if self.retry < 4:
                return self.run_command()
