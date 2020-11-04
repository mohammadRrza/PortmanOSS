import abc


class BaseCommand(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run_command(self):
        raise NotImplementedError()
