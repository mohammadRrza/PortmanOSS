import telnetlib
import time
from socket import error as socket_error
import re

def process_telnet_option(tsocket, command, option):
    from telnetlib import IAC, DO, DONT, WILL, WONT, SB, SE, TTYPE, NAWS, LINEMODE, ECHO
    tsocket.sendall(IAC + WONT + LINEMODE)

tn = telnetlib.Telnet('192.168.71.154', timeout=5)
tn.set_option_negotiation_callback(process_telnet_option)

index, match_obj, text = tn.expect(
            ['[U|u]sername: ', '[L|l]ogin:', '[L|l]oginname:', '[P|p]assword:'])

if index == 1:
    tn.write('{0}\r\n'.format('an2100'))

data = tn.read_until('User Name:', 5)
tn.write(("an2200\r\n").encode('utf-8'))
tn.read_until('Password:', 5)
tn.write(( "an2200\r\n").encode('utf-8'))

data = tn.read_until('>', 5)
tn.write(("showcard\r\n").encode('utf-8'))
data = tn.read_until('>', 5)
rows = data.split('\n')
cards = {}
for row in rows:
    items = row.split()
    if items[0] == '0':
        card_number, card_type = items[1:3]
        if '-' in card_type:
            card_type = None
        cards[card_number] = dict(card_number=card_number, card_type=card_type)
time.sleep(1)
tn.write(("version\r\n").encode('utf-8'))
data = tn.read_until('>', 5)
for item in re.findall('\d+\s+\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\s+\d+', data):
    card_number, hw_version, fw_version = item.split()[1:4]
    cards[card_number]['fw_version'] = fw_version
    cards[card_number]['hw_version'] = hw_version

for key, values in cards.iteritems():
    print key, values
