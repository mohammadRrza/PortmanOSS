import time
class DSLAMStatus(object):
    __slots__ = ['dslam_data', 'created_at',
                 'finished_at', 'result', 'error']

    def __init__(self, dslam_data):
        self.dslam_data = dslam_data
        self.created_at = time.time()
        self.finished_at = None
        self.result = None
        self.error = None

    def __repr__(self):
        return 'DSLAMInit Task: %s Created:%s End:%s'%(
            self.dslam_data['name'], self.created_at,
            self.finished_at
        )
