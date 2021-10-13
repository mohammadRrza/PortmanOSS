import abc


class BaseCommand(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def run_command(self):
        raise NotImplementedError()
