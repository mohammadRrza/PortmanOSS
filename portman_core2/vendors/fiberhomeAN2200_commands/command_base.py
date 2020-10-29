import abc


class BaseCommand(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run_command(self):
        raise NotImplementedError()

    @abc.abstractproperty
    def HOST(self):
        raise NotImplementedError()

    @HOST.setter
    def HOST(self, value):
        raise NotImplementedError()

    @abc.abstractproperty
    def telnet_username(self):
        raise NotImplementedError()

    @HOST.setter
    def telnet_username(self, value):
        raise NotImplementedError()

    @abc.abstractproperty
    def telnet_password(self):
        raise NotImplementedError()

    @HOST.setter
    def telnet_password(self, value):
        raise NotImplementedError()
