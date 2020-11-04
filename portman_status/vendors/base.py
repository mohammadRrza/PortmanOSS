class BaseDSLAM(object):

    def update_port_index_mapping(self):
        raise NotImplementedError()

    def get_current_port_status(self, port_name):
        raise NotImplementedError()

    def change_port_admin_status(self, port_name, admin_status):
        raise NotImplementedError()
