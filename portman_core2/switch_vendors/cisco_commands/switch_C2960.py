from .command_factory import CommandFactory
from .C2960_commands.show_dot1x import ShowDot1x
from .C2960_commands.show_ip_dhcp_snooping import ShowIpDhcpSnooping
from .C2960_commands.show_inventory import ShowInventory
from .C2960_commands.show_run import ShowRun
from .C2960_commands.show_vlan_brief import ShowVlanBrief


class C2960:
    command_factory = CommandFactory()
    command_factory.register_type('show dot1x', ShowDot1x)
    command_factory.register_type('show ip dhcp snooping', ShowIpDhcpSnooping)
    command_factory.register_type('show inventory', ShowInventory)
    command_factory.register_type('Get BackUp', ShowRun)
    command_factory.register_type('show vlan brief', ShowVlanBrief)

    def __init__(self):
        pass

    @classmethod
    def execute_command(cls, switch_data, command, params):
        print(switch_data)
        params['switch_id'] = switch_data['id']
        params['switch_name'] = switch_data['name']
        params['switch_ip'] = switch_data['ip']
        params['switch_fqdn'] = switch_data['fqdn']
        params['switch_type'] = switch_data['switch_type']
        params['SSH_username'] = switch_data['SSH_username']
        params['SSH_password'] = switch_data['SSH_password']
        command_class = cls.command_factory.get_type(command)(params)
        return command_class.run_command()
