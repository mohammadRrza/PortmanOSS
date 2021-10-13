import telnetlib
import time
from socket import error as socket_error
import re
from base_command import BaseCommand

class GetDSLAMBoard(BaseCommand):
    __slot__ = ('tn', 'fiberhomeAN3300_q', 'dslam_id', 'slot_number')
    def __init__(self, tn, params, fiberhomeAN3300_q=None):
        self.tn = tn
        self.fiberhomeAN3300_q = fiberhomeAN3300_q
        self.dslam_id = params.get('dslam_id')


    def run_command(self, protocol):
        try:
            self.tn.write("cd device\r\n")
            time.sleep(1)

            self.tn.write("show slot \r\n")
            for item in range(4):
                time.sleep(1)
                self.tn.write("\r\n")
            self.tn.write("end\r\n")
            result = self.tn.read_until("end\r\n")
            cards = {}
            for item in re.findall('\d+\s+\w+\s+\w+\s+(?:\S+)?', result):
                card_number, card_status, socket_status, card_type = item.split()
                if card_status == 'up':
                    card_status = 'active'
                else:
                    card_status = 'deactive'
                cards[card_number] = dict(status=card_status, card_type=card_type, card_number=card_number)
            '''
            time.sleep(1)
            tn.write("show temperature_alarm_information \r\n")
            tn.write("end\r\n")
            result=tn.read_until("end\r\n")
            temperature = re.search("temperature:(\d+)", result).groups()[0]
            time.sleep(1)
            '''
            self.tn.write("show version \r\n")
            for item in range(4):
                time.sleep(1)
                self.tn.write("\r\n")
            self.tn.write("end\r\n")
            result = self.tn.read_until("end\r\n")
            for card_number, fw_version, hw_version in re.findall('(?P<card_number>\d+)\s+\S+\s+(?P<fw>V\s(?:\d+|\.)*)\s+(?P<hw>V\s(?:\d+|\.)*)', result):
                cards[card_number]['fw_version'] = fw_version
                cards[card_number]['hw_version'] = hw_version

            for item in re.findall('(?P<card_number>\d+)\s+\S+\s+(?P<fw>R(?:\d+|\.)*)\s+(?P<hw>(\S)+)', result):
                card_number, fw_version, hw_version = item[0:3]
                cards[card_number]['fw_version'] = fw_version
                cards[card_number]['hw_version'] = hw_version

            result = {'result': cards.values()}
            print '+++++++++++++++++++++++++++++'
            print result
            print '+++++++++++++++++++++++++++++'
            if protocol == 'http':
                return result
            elif protocol == 'socket':
                self.fiberhomeAN2200_q.put(("update_dslam_board",
                self.dslam_id,
                result))
        except Exception as ex:
            print ex
            return {'result': 'error: show fdb slot command'}
