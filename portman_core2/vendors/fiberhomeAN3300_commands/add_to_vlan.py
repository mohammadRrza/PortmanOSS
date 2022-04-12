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
        self.port_conditions = params.get('port_conditions')
        self.port_index = params.get('port_indexes')[0]
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
            count = 1
            res = ''
            vlan_info = {}
            vlan_info['vlan_id'] = None
            all_pvc = []
            pvc_num = None
            profile_name = None
            tn = telnetlib.Telnet(self.__HOST)
            tn.write((self.__telnet_username + "\r\n").encode('utf-8'))
            tn.write((self.__telnet_password + "\r\n").encode('utf-8'))
            tn.write(b"end\r\n")
            err1 = tn.read_until(b"end")
            if "Login Failed." in str(err1):
                return "Telnet Username or Password is wrong! Please contact with core-access department."
            tn.read_until(b"User>")
            tn.write(b'admin\r\n')
            tn.read_until(b"Password:")
            tn.write('{0}\r\n'.format(self.__access_name).encode('utf-8'))
            time.sleep(0.5)
            err1 = tn.read_until(b"#", 1)
            if "Bad Password..." in str(err1):
                return "DSLAM Password is wrong!"
            ################## Show Port Command #########################
            tn.write(b"cd device\r\n")
            tn.write("show port {0}:{1}\r\n\r\n".format(self.port_index['slot_number'],
                                                        self.port_index['port_number']).encode('utf-8'))
            time.sleep(0.1)
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            tn.write(b"\r\n")
            time.sleep(0.1)
            tn.write(b"end\r\n")
            result = tn.read_until(b"end")
            if "Invalid port list" in str(result):
                str_res = ["There is one of the following problems:", "This card is not configured",
                           "No card is defined on this port", "Card number is out of range.",
                           "Port number is out of range."]
                return str_res

            result = str(result).split("\\r\\n")
            result = [re.sub(r'\s+--P[a-zA-Z +\\1-9[;-]+H', '', val) for val in result if
                      re.search(r'\s{3,}', val)]
            tn.read_until(b'#')
            for val in result:
                if 'Profile Name' in val:
                    profile_name = val.split(":")[1].strip()
            ######################### Show All Vlans ########################
            tn.write(b"cd vlan\r\n")
            tn.write(b"show pvc vlan\r\n")
            time.sleep(0.5)
            tn.read_until(b'#', 0.5)
            output = tn.read_until(b'stop--', 3)
            res += str(output)

            """
            If fiberhomeAn3300 is type 2 , run under commands

            """

            if "Unknown command." in res:
                vlan_info['vlan_id'] = self.__vlan_id
                vlan_info['vlan_name'] = self.__vlan_name
                tn.write("show service vlan slot {0} port {1}\r\n".format(self.port_index['slot_number'],
                                                                          self.port_index['port_number']).encode(
                    'utf-8'))
                time.sleep(0.5)
                output = tn.read_until(b'#')
                output = str(output).split("\\r\\n")
                vlan_info['pvc_num'] = output[2].split()[2]

                tn.write(b"show localvlan\r\n")
                output = tn.read_until(b"stop--", 0.2)
                res1 = ''
                res1 += str(output)
                while '#' not in str(output):
                    tn.write(b'\r\n')
                    output = tn.read_until(b'#', 0.1)
                    res1 += str(output)
                    ##################### Add a new Vlan #####################
                if f":{self.__vlan_name}" not in res1:
                    tn.write("create localvlan {0}\r\n".format(self.__vlan_name).encode('utf-8'))
                    time.sleep(0.2)
                    tn.write("set localvlan {0} tag {1}\r\n".format(self.__vlan_name, self.__vlan_id).encode('utf-8'))
                    time.sleep(0.2)
                    tn.write("set localvlan {0} add uplinkport 29:1-29:7 tagged\r\n".format(self.__vlan_name).encode('utf-8'))

            """
                If fiberhomeAn3300 is type 1 , run under commands

            """
            if vlan_info['vlan_id'] == None:
                while '#' not in str(output):
                    print('----------------------------------------')
                    print(count)
                    print('----------------------------------------')
                    count += 1
                    tn.write(b'\r\n')
                    output = tn.read_until(b'#', 0.1)
                    res += str(output)
                tn.write(b"end\r\n")
                result = tn.read_until(b"end")
                res += str(result)
                res = res.replace("'b'", "")
                result = str(res).split("\\r\\n")
                result = [re.sub(r"\s+--P[a-zA-Z +\\1-9[;-]+H", '', val) for val in result if
                          re.search(r'\s{4,}[-\d\w]|-{5,}', val)]
                if "information" not in result[0]:
                    return result
                ################# get vlan name, vlan ID and pvc number due to Card and Port. ################
                cart_port = [val.split() for val in result]
                flag = 0
                for item in reversed(cart_port):
                    if item[0] == str(self.port_index['slot_number']) and item[1] == str(
                            self.port_index['port_number']):
                        vlan_info['pvc_num'] = item[2]
                        flag = 1
                    if 'vlan' in item and flag == 1:
                        vlan_info['vlan_id'] = item[2].split(":")[1]
                        vlan_info['vlan_name'] = item[1].split(":")[1]
                        break
            check_directory = tn.read_until(b'profile#', 0.1)

            ################################ Show PVC command ###############################
            while 'profile#' not in str(check_directory):
                tn.write(b'cd profile\r\n')
                check_directory = tn.read_until(b'profile#', 0.1)
            tn.write("show dsl-profile {0}\r\n".format(profile_name).encode('utf-8'))
            time.sleep(0.2)
            pvc_res = ''
            output = tn.read_until(b'profile#', 0.1)
            pvc_res += str(output)
            while 'profile#' not in str(output):
                tn.write(b'\r\n')
                output = tn.read_until(b'profile#', 0.1)
                pvc_res += str(output)
            tn.write(b"end")
            result = tn.read_until(b"end")
            pvc_res += str(result)
            if "not exist." in str(result):
                return f"Profile {profile_name} does not exist."
            if 'pvc' in str(pvc_res):
                result = str(pvc_res).split("\\r\\n")
                result = [re.sub(r'\s+--P[a-zA-Z +\\1-9[;-]+H', '', val) for val in result if
                          re.search(r'pvc\d|vpi|vci', val)]
                for inx, val in enumerate(result):
                    if "pvc" in val:
                        temp = {}
                        temp[val.split(':')[0].strip()] = {}
                        temp[val.split(":")[0].strip()]['vpi'] = result[inx + 1].split(":")[1]
                        temp[val.split(":")[0].strip()]['vci'] = result[inx + 2].split(":")[1]
                        all_pvc.append(temp)
            else:
                result = str(result).replace("\\t", "    ")
                result = str(result).split("\\r\\n")
                result = [re.sub(r'\s+--P[a-zA-Z +\\1-9[;-]+H', '', val) for val in result if
                          re.search(r':', val)]
                return result

            ############################## Get user PVC ##############################
            for item in all_pvc:
                for key, value in item.items():
                    if int(value['vpi']) == self.__vpi and int(value['vci']) == self.__vci:
                        pvc_num = key[-1]
            ############################## Delete PVC Vlan ##############################
            check_directory = tn.read_until(b'vlan#', 0.1)
            while 'vlan#' not in str(check_directory):
                tn.write(b'cd vlan\r\n')
                check_directory = tn.read_until(b'vlan#', 0.1)
            """
                If fiberhomeAn3300 is type 1 , run under commands
                
            """
            tn.write("set pvc vlan {0} delete slot {1} port {2} pvc {3} untagged\r\n".format(vlan_info['vlan_name'],
                                                                                             self.port_index[
                                                                                                 'slot_number'],
                                                                                             self.port_index[
                                                                                                 'port_number'],
                                                                                             vlan_info[
                                                                                                 'pvc_num']).encode('utf-8'))

            ############################## Add PVC Vlan ##############################
            tn.write("set pvc vlan {0} add slot {1} port {2} pvc {3} untagged\r\n".format(self.__vlan_name,
                                                                                          self.port_index[
                                                                                              'slot_number'],
                                                                                          self.port_index[
                                                                                              'port_number'],
                                                                                          pvc_num).encode('utf-8'))
            tn.write(b"end\r\n")
            result = tn.read_until(b"end")
            if "not existed." in str(result):
                tn.write("create pvc vlan {0}\r\n".format(self.__vlan_name).encode('utf-8'))
                time.sleep(0.2)
                tn.write(
                    "set pvc vlan {0} tag {1}\r\n".format(self.__vlan_name, self.__vlan_id).encode('utf-8'))
                time.sleep(0.2)
                tn.write("set pvc vlan {0} add uplink 29:1-29:7 tagged\r\n".format(self.__vlan_name).encode('utf-8'))
                time.sleep(0.2)
                tn.write("set pvc vlan {0} add slot {1} port {2} pvc {3} untagged\r\n".format(self.__vlan_name,
                                                                                              self.port_index[
                                                                                                  'slot_number'],
                                                                                              self.port_index[
                                                                                                  'port_number'],
                                                                                              pvc_num).encode('utf-8'))
            """
            If fiberhomeAn3300 is type 2 , run under commands
            
            """
            ############################## Delete PVC Vlan ##############################
            if "invalid now" in str(result):
                tn.write("delete service vlan slot {0} port {1} pvc {2} index 1\r\n".format(
                    self.port_index['slot_number'], self.port_index['port_number'], vlan_info['pvc_num']).encode(
                    'utf-8'))

                ############################## Add PVC Vlan ##############################
                tn.write("set service vlan slot {0} port {1} pvc {2} index 1 svid {3} cvid 0 untagged\r\n".format(
                    self.port_index['slot_number'], self.port_index['port_number'], pvc_num,
                    self.__vlan_id).encode('utf-8'))
            if "has been add" in str(result):
                return dict(
                    result=f"slot {self.port_index['slot_number']} port {self.port_index['port_number']} pvc {pvc_num} has been successfully add to vlan {self.__vlan_name}",
                    status=200)
            tn.close()
            return dict(
                result=f"slot {self.port_index['slot_number']} port {self.port_index['port_number']} pvc {pvc_num} has been successfully add to vlan {self.__vlan_name}",
                status=200)

        except (EOFError, socket_error) as e:
            print(e)
            self.retry += 1
            if self.retry < 4:
                return self.run_command()

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return str(ex) + "  // " + str(exc_tb.tb_lineno)
