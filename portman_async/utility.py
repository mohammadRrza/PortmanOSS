import jsonrpclib


def dslam_port_run_command(dslam_id, command, params):
    c = jsonrpclib.Server('http://localhost:7060')
    return c.add_command(dslam_id, command, params)