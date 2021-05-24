from .command_factory import CommandFactory
from .C2960_commands.show_dot1x import ShowDot1x


class C2960:
    def __init__(self):
        pass

    @classmethod
    def execute_command(cls, switch_data, command, params):
        switch_id = switch_data['id']
        switch_name = switch_data['name']
        switch_ip = switch_data['ip']
        switch_fqdn = switch_data['fqdn']
        switch_type = switch_data['switch_type']
        return 'ssssss'
