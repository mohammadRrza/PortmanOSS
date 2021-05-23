class PortmanFactory:
    def __init__(self):
        self.__resource_types = {}  # name:class

    def register_type(self, name, klass):


        if name in self.__resource_types:
            raise Exception('Resource Type {0} Already Registered!'.format(name))

        self.__resource_types[name] = klass
        print('===================================')
        print(klass)
        print(name)
        print(self.__resource_types)
        print('===================================')
    def get_type(self, name):

        if 'C2960' in self.__resource_types:
            return self.__resource_types['C2960']
        print('ggggggggggggggggggggggggggggggggggggggggg')
        print(name)
        print(self.__resource_types['C2960'])
        print('ggggggggggggggggggggggggggggggggggggggggggggg')
        raise Exception('Resource Type "%s" is Not Registered!' % name)
