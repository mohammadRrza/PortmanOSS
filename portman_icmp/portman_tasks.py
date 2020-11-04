import time
class DSLAMICMPTask(object):
    __slots__ = ['dslam_data', 'created_at', 'ping_count', 'ping_timeout',
                 'finished_at', 'result', 'error']

    def __init__(self, dslam_data, ping_count, ping_timeout):
        self.dslam_data = dslam_data
        self.ping_count = ping_count
        self.ping_timeout = ping_timeout
        self.created_at = time.time()
        self.finished_at = None
        self.result = None
        self.error = None

    def __repr__(self):
        return 'DSLAMInit Task: %s Created:%s End:%s'%(
            self.dslam_data['name'], self.created_at,
            self.finished_at
        )
