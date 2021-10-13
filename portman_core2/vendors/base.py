class BaseDSLAM(object):

    def update_port_index_mapping(self):
        raise NotImplementedError()

    def get_current_port_status(self, slot_number, port_number):
        raise NotImplementedError()

    def change_port_admin_status(self, slot_number, port_number, admin_status):
        raise NotImplementedError()
