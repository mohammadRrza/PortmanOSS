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


def router_run_command(router_id, command, params):
    c = jsonrpclib.Server('http://localhost:7060')
    return c.router_run_command(router_id, command, params)
