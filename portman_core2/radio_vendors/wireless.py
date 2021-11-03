from .command_factory import CommandFactory

from .wireless_commands.set_radio_geographical_coordinates import SetRadioGeographicalCoordinates


class Wireless:
    command_factory = CommandFactory()
    command_factory.register_type('set coordinates', SetRadioGeographicalCoordinates)

    def __init__(self):
        pass

    @classmethod
    def execute_command(cls, router_data, command, params):
        params['router_id'] = router_data['id']
        params['router_name'] = router_data['name']
        params['router_ip'] = router_data['ip']
        params['router_fqdn'] = router_data['fqdn']
        params['radio_type'] = router_data['radio_type']
        params['SSH_username'] = router_data['SSH_username']
        params['SSH_password'] = router_data['SSH_password']
        params['SSH_port'] = router_data['SSH_port']
        params['SSH_timeout'] = router_data['SSH_timeout']

        command_class = cls.command_factory.get_type(command)(params)
        return command_class.run_command()
