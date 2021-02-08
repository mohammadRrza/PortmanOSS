from .command_factory import CommandFactory
from .cisco_commands.C2960_commands.show_dot1x import ShowDot1x


class C2960:
    def __init__(self):
        pass

    command_factory = CommandFactory()
    command_factory.register_type('show dot1x', ShowDot1x)
