import jsonrpclib
from socket import error as SocketError


def shutdown_portman(self):
    c = jsonrpclib.Server('http://localhost:7060')
    try:
        c.shutdown_portman()
    except SocketError as ex:
        return 'PortmanCore is shutdown'
    except Exception as ex:
        return 'give error when shuttdown PortmanCore'


def switch_run_command(switch_id, command, params):
    c = jsonrpclib.Server('http://localhost:7060')
    return c.switch_run_command(switch_id, command, params)

def run_icmp_command(switch_id, icmp_type, params=None):
    c = jsonrpclib.Server('http://localhost:7070')
    return c.run_icmp_command(switch_id, icmp_type, params)