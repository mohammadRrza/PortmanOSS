import jsonrpclib
import json
class EventManager(object):
    def __init__(self, clients):
        self.clients = clients

    def send_message(self, msg):
        if type(msg[2]).__name__ == 'long':
            return True
        result = msg[2]
        socket_id = result
        if socket_id:
            try:
                self.clients.get(socket_id).send_message(msg)
            except Exception as ex:
                print('---------------------------------')
                print(ex)
                print('---------------------------------')
                self.shutdown_socket(msg[1], socket_id)

    def shutdown_socket(self, channel, socket_id):
        if channel == 'ping':
            c = jsonrpclib.Server('http://localhost:7070')
            result = c.shutdown_ping_command(socket_id)
        elif channel == 'port_status':
            c = jsonrpclib.Server('http://localhost:7060')
            result = c.shutdown_port_status_periodic(socket_id)
            print(result)



