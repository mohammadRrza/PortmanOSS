# import os
# import sys
# import ldap
# sys.path.insert(0, '/home/sajad/Project/portmanv3/portman_web/')
#
# os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
# import django
# django.setup()
# from django_auth_ldap.backend import LDAPBackend
#
#
# class MyLDAPBackend(LDAPBackend):
#     """ A custom LDAP authentication backend """
#
#     def authenticate(self, username, password):
#         """ Overrides LDAPBackend.authenticate to add custom logic """
#         try:
#             user = LDAPBackend().authenticate(self, username, password)
#             print(user)
#             """ Add custom logic here """
#
#             return user
#         except Exception as e:
#             print(e)

import ldap

from portman_web.config import settings


def ldap_auth(username, password):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    try:
        ldap.set_option(ldap.OPT_REFERRALS, 0)
        ldap.initialize_fd()
        #ldap.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        conn.simple_bind_s(username, password)
    except ldap.LDAPError as e:
        return f'failed to authenticate'

    conn.unbind_s()
    return "Success"


if __name__ == "__main__":
    user = ldap_auth('', '')
    print(user)
    # x = MyLDAPBackend()
    # x.authenticate('sajad saedi', 'Saida@71@')
