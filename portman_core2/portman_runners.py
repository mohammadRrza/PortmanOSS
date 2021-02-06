# -*- coding:UTF8 -*-
import time


class DSLAMBulkCommand(object):
    """
    To initialize ports' status on a dslam (first operation after adding a dslam)
    """
    __slots__ = ['title', 'commands', 'created_at', 'finished_at',
            'result', 'error', 'conditions']

    def __init__(self, title, commands, conditions):
        self.title = title
        self.commands = commands
        self.conditions = conditions
        self.created_at = time.time()
        self.finished_at = None
        self.result = None
        self.error = None


class DSLAMPortCommandTask(object):
    """
    To initialize ports' status on a dslam (first operation after adding a dslam)
    """
    __slots__ = ['dslam_data', 'command', 'params', 'created_at',
            'finished_at', 'result', 'error']

    def __init__(self, dslam_data, command, params):
        self.dslam_data = dslam_data
        self.command = command
        self.params = params
        self.created_at = time.time()
        self.finished_at = None
        self.result = None
        self.error = None


class RouterCommandTask(object):

    def __init__(self, router_data, command, params):
        self.router_data = router_data
        self.command = command
        self.params = params
        self.created_at = time.time()
        self.finished_at = None
        self.result = None
        self.error = None

class SwitchCommandTask(object):

    def __init__(self, switch_data, command, params):
        self.switch_data = switch_data
        self.command = command
        self.params = params
        self.created_at = time.time()
        self.finished_at = None
        self.result = None
        self.error = None

class DSLAMInitTask(object):
    """
    To initialize ports' status on a dslam (first operation after adding a dslam)
    """
    __slots__ = ['dslam_data', 'created_at',
                 'finished_at', 'result', 'error']

    def __init__(self, dslam_data):
        self.dslam_data = dslam_data
        self.created_at = time.time()
        self.finished_at = None
        self.result = None
        self.error = None

    def __repr__(self):
        return 'DSLAMInit Task: %s Created:%s End:%s' % (
            self.dslam_data['name'], self.created_at,
            self.finished_at
        )


class PortInfoSyncTask(object):
    """
    For updating ports' status on a dslam in bulk
    """
    __slots__ = ['dslam_data', 'dslam_port_map', 'created_at',
                 'finished_at', 'result', 'error']

    def __init__(self, dslam_data, dslam_port_map):
        self.dslam_data = dslam_data
        self.dslam_port_map = dslam_port_map
        self.created_at = time.time()
        self.finished_at = None
        self.result = None
        self.error = None

    def __repr__(self):
        return 'DSLAMUpdate Task: %s Created:%s End:%s' % (
            self.dslam_data['name'], self.created_at,
            self.finished_at
        )


class DSLAMPortLineProfileChangeTask(object):
    __slots__ = ['dslam_data', 'port_index',
                 'new_lineprofile', 'result', 'error']

    def __init__(self, dslam_data, port_index, new_lineprofile):
        self.dslam_data = dslam_data
        self.port_index = port_index
        self.new_lineprofile = new_lineprofile
        self.result = None
        self.error = None


class DSLAMPortStatusInfoTask(object):
    __slots__ = ['dslam_data', 'port_index',
                 'result', 'error']

    def __init__(self, dslam_data, port_index):
        self.dslam_data = dslam_data
        self.port_index = port_index
        self.result = None
        self.error = None


class DSLAMPortAdminStatusChangeTask(object):
    __slots__ = ['dslam_data', 'port_index', 'new_status',
                 'result', 'error']

    def __init__(self, dslam_data, port_index, new_status):
        self.dslam_data = dslam_data
        self.port_index = port_index
        self.new_status = new_status
        self.result = None
        self.error = None


class DSLAMPortResetAdminStatusInfoTask(object):
    __slots__ = ['dslam_data', 'port_index',
                 'result', 'error']

    def __init__(self, dslam_data, port_index):
        self.dslam_data = dslam_data
        self.port_index = port_index
        self.result = None
        self.error = None
