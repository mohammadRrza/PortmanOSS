import dj_bridge
from dj_bridge import DSLAM

import tornado.websocket
from tornado.ioloop import IOLoop
from tornado.options import options, define, parse_command_line
from toredis import Client

import jsonrpclib
import uuid
import json
from datetime import datetime
from event_manager import EventManager

define("port", default=2083, type=int)


class ShutdownPingHandler(tornado.web.RequestHandler):
    def post(self):
        socket_id = self.get_argument('socket_id')
        if socket_id:
            c = jsonpclib.Server('http://localhost:7070')
            result = c.shutdown_ping_command(socket_id)
            return result
        return 'socket_id is not exist'


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    clients = {}

    def check_origin(self, origin):
        return True

    def open(self, *args):
        self.stream.set_nodelay(True)
        self.user = None
        self.last_action = datetime.now()
        self.socket_id = uuid.uuid4().hex
        WebSocketHandler.clients[self.socket_id] = self

    def send_message(self, msg):
        try:
            self.write_message(json.dumps(msg[2]))
            self.last_action = datetime.now()
        except Exception as ex:
            print(ex)

    def on_message(self, message):
        print(message)
        msg = json.loads(json.loads(message).get('message'))

        action = msg.get('action')
        dslam_id = msg.get('dslam_id')
        params = msg.get('params')

        if not action:
            pass

        if not params:
            pass

        if action == 'ping':
            self.ping_request(dslam_id, params)
        elif action == 'port_status':
            self.get_port_status(dslam_id, params)

    def on_close(self):
        if self.socket_id in WebSocketHandler.clients:
            print("Connection closed")
            del WebSocketHandler.clients[self.socket_id]

    def get_port_status(self, dslam_id, params):
        port = params.get('port')
        params = {'port': port, 'channel': 'port_status', 'socket_id': self.socket_id}
        c = jsonrpclib.Server('http://localhost:7060')
        c.get_port_status(dslam_id, params)

    def ping_request(self, dslam_id, params=None):
        if params:
            count = params.get('count')
            timeout = params.get('timeout')
            if not count:
                count = 4
            if not timeout:
                timeout = 0.2
        else:
            count = 4
            timeout = 0.2
        c = jsonrpclib.Server('http://localhost:7070')
        params = {'count': count, 'timeout': timeout, 'channel': 'ping', 'socket_id': self.socket_id}
        c.run_icmp_command(dslam_id, 'ping', params)


app = tornado.web.Application([
    (r'/ws/', WebSocketHandler),
    (r'/ping/shutdown/', ShutdownPingHandler),
])

event_manager = EventManager(WebSocketHandler.clients)


def process_message(msg):
    event_manager.send_message(msg)


if __name__ == '__main__':
    app.listen(options.port)
    client = Client()
    client.connect()
    client.subscribe("ping", callback=process_message)
    client.subscribe("port_status", callback=process_message)
    IOLoop.instance().start()
