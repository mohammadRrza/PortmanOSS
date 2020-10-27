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

def bulk_command(title, commands, conditions):
    c = jsonrpclib.Server('http://localhost:7060')
    return c.bulk_commands(title, commands, conditions)


def dslam_port_run_command(dslam_id, command, params):
    c = jsonrpclib.Server('http://localhost:7060')
    return c.add_command(dslam_id, command, params)


def scan_dslamport(dslam_id):
    c = jsonrpclib.Server('http://localhost:7060')
    return c.scan_dslamport(dslam_id)


def scan_dslam_general_info(dslam_id):
    c = jsonrpclib.Server('http://localhost:7080')
    c.general_update(dslam_id)

    c = jsonrpclib.Server('http://localhost:7070')
    c.run_icmp_command(dslam_id, 'ping', {'count': 4, 'timeout': 0.2})
    c.run_icmp_command(dslam_id, 'traceroute')
    return 'dslam general information is updating'


def get_port_info(dslam_id, port_id):
    c = jsonrpclib.Server('http://localhost:7060')
    return c.get_port_info(dslam_id, port_id)


def change_port_admin_status(dslam_id, port_id, new_status):
    c = jsonrpclib.Server('http://localhost:7060')
    return c.change_port_admin_status(dslam_id, port_id, new_status)


def reset_admin_status(dslam_id, port_id):
    c = jsonrpclib.Server('http://localhost:7060')
    return c.reset_admin_status(dslam_id, port_id)


def change_port_line_profile(dslam_id, port_id, new_line_profile):
    c = jsonrpclib.Server('http://localhost:7060')
    return c.change_port_line_profile(dslam_id, port_id, new_line_profile)


def run_icmp_command(dslam_id, icmp_type, params=None):
    c = jsonrpclib.Server('http://localhost:7070')
    return c.run_icmp_command(dslam_id, icmp_type, params)
