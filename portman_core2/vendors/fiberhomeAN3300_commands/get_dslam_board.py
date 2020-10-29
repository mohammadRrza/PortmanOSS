import telnetlib
import time
from socket import error as socket_error
import re
tn = telnetlib.Telnet('192.168.51.138')
tn.write(("wri\r\n").encode('utf-8'))
tn.read_until("Password: ")
tn.write(("an3300\r\n").encode('utf-8'))
time.sleep(1)

tn.write("admin\r\n")
tn.write(("an3300\r\n").encode('utf-8'))
time.sleep(1)
tn.write("cd device\r\n")
time.sleep(1)

tn.write("show slot \r\n")
for item in range(4):
    time.sleep(1)
    tn.write("\r\n")
tn.write("end\r\n")
result=tn.read_until("end\r\n")
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
tn.write("show version \r\n")
for item in range(4):
    time.sleep(1)
    tn.write("\r\n")
tn.write("end\r\n")
result = tn.read_until("end\r\n")
for card_number, fw_version, hw_version in re.findall('(?P<card_number>\d+)\s+\S+\s+(?P<fw>V\s(?:\d+|\.)*)\s+(?P<hw>V\s(?:\d+|\.)*)', result):
    cards[card_number]['fw_version'] = fw_version
    cards[card_number]['hw_version'] = hw_version

for item in re.findall('(?P<card_number>\d+)\s+\S+\s+(?P<fw>R(?:\d+|\.)*)\s+(?P<hw>(\S)+)', result):
    card_number, fw_version, hw_version = item[0:3]
    cards[card_number]['fw_version'] = fw_version
    cards[card_number]['hw_version'] = hw_version
for key, value in cards.iteritems():
    print key, value
tn.write("exit\r\n")
tn.write("y\r\n")
