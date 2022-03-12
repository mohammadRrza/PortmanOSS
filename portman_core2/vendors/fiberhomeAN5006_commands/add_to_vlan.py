import sys
import telnetlib
import time
from socket import error as socket_error
from .command_base import BaseCommand
import re


class AddToVlan(BaseCommand):
    def __init__(self, params=None):
        self.__HOST = None
        self.__telnet_username = None
        self.__telnet_password = None
        self.__vlan_name = params.get('vlan_name')
        self.__vlan_id = params.get('vlan_id')
        self.__vpi = params.get('vpi')
        self.__vci = params.get('vci')
        self.__access_name = params.get('access_name', 'an3300')
        self.port_index = params.get('port_indexes')[0]

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
            uplink_vlans_id = []
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            err1 = tn.read_until(b"#", 1)
            if "Login Failed." in str(err1):
                return dict(result="Telnet Username or Password is wrong! Please contact with core-access department.", status=500)

            ############################## Check if vlan exist ##############################
            tn.write(b"cd vlan\r\n")
            tn.write(b'show uplink vlan\r\n')
            tn.write(b"end\r\n")
            result = tn.read_until(b"end")
            result = [re.sub(r'(\w+\s){3,}:\s\d+\s+', '', val) for val in str(result).split('\\r\\n') if
                      re.search(r'\s{4,}', val)]
            for vlan in result[1:]:
                uplink_vlans_id.append(vlan.split()[2])
            uplink_card_port = result[1].split()[4]
            if self.__vlan_id not in uplink_vlans_id:
                tn.write("add uplink vlan {0} start {1} end {1} tag portno {2} type non-voip\r\n".format(
                    self.__vlan_name, self.__vlan_id, uplink_card_port).encode('utf-8'))

            ######################## Remove Card and Port from specific vlan ########################
            tn.write("clear vlan service interface {0}/{1}\r\n".format(self.port_index['slot_number'],
                                                                       self.port_index['port_number']).encode('utf-8'))
            tn.write(b"end\r\n")
            result = tn.read_until(b"end")
            if "unknown input" in str(result):
                str_res = ["There is one of the following problems:", "This card is not configured",
                           "Card number is out of range.", "Port number is out of range."]
                return dict(result=str_res, status=500)

            ########################### Add card and port to the new Vlan ###########################
            tn.write("add vlan service type unicast mode tag vid {0} cos 0 interface {1}/{2}/0\r\n".format(
                self.__vlan_id,
                self.port_index[
                    'slot_number'],
                self.port_index[
                    'port_number']).encode('utf-8'))
            tn.write(b'cd ..\r\n')
            tn.write(b'cd dsl\r\n')
            tn.write(
                "attach pvc profile name {0}-{1} interface {2}/{3}".format(self.__vpi, self.__vci,
                                                                           self.port_index['slot_number'],
                                                                           self.port_index['port_number']).encode(
                    'utf-8'))
            tn.write(b"\r\n")
            tn.write(b"end\r\n")
            tn.write(b"exit\r\n")
            tn.close()
            final_result = f"slot {self.port_index['slot_number']} port {self.port_index['port_number']} pvc 0 has been successfully added to vlan {self.__vlan_name}"
            return dict(result=final_result, status=200)

        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return str(ex) + "  // " + str(exc_tb.tb_lineno)
