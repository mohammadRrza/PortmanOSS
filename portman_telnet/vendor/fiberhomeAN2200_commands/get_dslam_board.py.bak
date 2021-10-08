import telnetlib
import re
import time
from base_command import BaseCommand

class GetDSLAMBoard(BaseCommand):
    __slot__ = ('tn', 'fiberhomeAN2200_q', 'dslam_id')
    def __init__(self, tn, params, fiberhomeAN2200_q=None):
        self.tn = tn
        self.dslam_id = params.get('dslam_id')
        self.fiberhomeAN2200_q = fiberhomeAN2200_q

    def run_command(self, protocol):
        print 'i here'
        self.tn.write(("showcard\r\n").encode('utf-8'))
        data = self.tn.read_until('>')
        print data
        if 'timeout' in data.lower():
            self.tn.close()
            raise ValueError('first please login session')
        results = []
        rows = data.split('\n')
        cards = {}
        for row in rows:
            items = row.split()
            if items[0] == '0':
                card_number, card_type = items[1:3]
                if '-' in card_type:
                    card_type = None
                cards[card_number] = dict(card_number=card_number, card_type=card_type)
        print cards
        time.sleep(1)
        self.tn.write(("version\r\n").encode('utf-8'))
        data = self.tn.read_until('>', 5)
        for item in re.findall('\d+\s+\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\s+\d+', data):
            card_number, hw_version, fw_version = item.split()[1:4]
            cards[card_number]['fw_version'] = fw_version
            cards[card_number]['hw_version'] = hw_version

        result = {"result": cards.values()}
        print '==================================='
        print result
        print '==================================='
        if protocol == 'http':
            return result
        elif protocol == 'socket':
            self.fiberhomeAN2200_q.put(("update_dslam_board",
                self.dslam_id,
                result))
