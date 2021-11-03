import pingparser
import subprocess
import redis
import json
from datetime import datetime
import time
from threading import Thread
import calendar

redis_conn = redis.Redis()


class ICMP(object):
    def __init__(self, django_orm_queue=None):
        self.__django_orm_queue = django_orm_queue
        self.redis = redis_conn
        self.repeat_ping = True

    def _update_dslam_icmp(self, task):
        host = task.dslam_data['ip']
        ping_dict_results = self.ping_request(task.dslam_data['id'], host, task.ping_count, task.ping_timeout)
        trace_route_result = self.trace_route_request(task.dslam_data['id'], host)
        self.__django_orm_queue.put(("update_dslam_icmp", task.dslam_data['id'], ping_dict_results, trace_route_result))

    def trace_route_request(self, dslam_id, host, channel=None):
        traceroute = subprocess.Popen(["mtr", '-n', '-w', '100', host], stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
        lst_trace_route_line = []
        for line in iter(traceroute.stdout.readline, ""):
            lst_trace_route_line.append(line.strip())
        if len(lst_trace_route_line) == 0:
            self.__django_orm_queue.put(("create_dslam_event",
                dslam_id,
                'dslam_trace_route_error',
                'DSLAM Trace Route Command is not working',
                'warning'))
            return None
        else:
            trace_route_result = '\r\n'.join(lst_trace_route_line)
            return trace_route_result

    def ping_request(self, dslam_id, host, ping_count, ping_timeout, channel=None, socket_id=None):
        ping_output = self.ping(host, ping_count, ping_timeout)
        ping_results = {}
        try:
            print(ping_output)
            ping_results = pingparser.parse(ping_output.decode('utf-8'))
        except Exception as ex:
            print('----------------------------------------')
            print(ex)
            print('----------------------------------------')

        try:
            if channel:
                thread = Thread(target=self.ping_channel, args=(host, ping_count, ping_timeout, channel, socket_id))
                thread.start()
                return 'write on channel'
            else:
                return dict(list(ping_results.items()))
        except Exception as ex:
            print('++++++++++++++++++++++++++++')
            print(ex)
            print('++++++++++++++++++++++++++++')
            ping_results = ping_results
            self.__django_orm_queue.put(("create_dslam_event",
                dslam_id,
                'dslam_ping_error',
                'Ping Command Result is None',
                'warning'))
            return None

    def ping_channel(self, host, ping_count, ping_timeout, channel, socket_id):
        while(self.repeat_ping):
            ping_results = pingparser.parse(self.ping(host, ping_count, ping_timeout))
            ping_results['socket_id'] = socket_id
            ping_results['timestamp'] = calendar.timegm(datetime.today().timetuple())
            self.redis.publish(channel, json.dumps(ping_results))
            time.sleep(5)
        print(('shutdown socket_id: ', socket_id))

    def ping(self, host, ping_count, ping_timeout):
        return subprocess.Popen(["/bin/ping", "-c" + str(ping_count), "-i" + str(ping_timeout), host,],
                                       stdout=subprocess.PIPE).stdout.read()

