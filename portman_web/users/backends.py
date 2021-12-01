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
import sys

import ldap

from portman_web.config import settings

LDAP_SERVER = 'ldap://172.28.238.238:389'
LDAP_BASE = "DC=pishgaman,DC=local"


def ldap_auth(username, password):
    conn = ldap.initialize(LDAP_SERVER)
    try:
        conn.protocol_version = ldap.VERSION3
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.simple_bind_s(username, password)
        x = conn.whoami_s()
        print(x)
        searchFilter = "(cn=sajad*)"
        retrieveAttributes = ['objectClass']
        y = conn.search_s(LDAP_BASE, ldap.SCOPE_SUBTREE, searchFilter)
        print(y)
    except ldap.LDAPError as e:
        return f'failed to authenticate'

    conn.unbind_s()
    return "Success"


# def users_ldap_groups(uid, username, password):
#     """ Returns a list of the groups that the uid is a member of.
#         Returns False if it can't find the uid or throws an exception.
#         It's up to the caller to ensure that the UID they're using exists!
#     """
    # logger.debug("uid: ", uid)
    # ignore certificate errors
    # ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    # l = ldap.initialize(LDAP_SERVER)
    # this search for all objectClasses that user is in.
    # change this to suit your LDAP schema
    # search_filter = '(|(&(objectClass=*)(member=uid=%s,OU=Users,OU=Software,OU=PTE-Staff,DC=pishgaman,DC=local)))' % uid

    # try:
        # this returns the groups!
        # l.simple_bind_s(username, password)
        # results = l.search_s(LDAP_BASE, ldap.SCOPE_SUBTREE, search_filter, ['cn', 'mail'])
        # print(results)
        # logger.debug('%s groups: %s' % (uid, results))
    #     return results
    # except ldap.NO_SUCH_OBJECT as e:
        # logger.error(
        #     "{}:{}unable to lookup uid {} on LDAP server {}: {}".format(__file__, sys._getframe().f_code.co_name, uid,
        #                                                                 LDAP_SERVER, e))
    #     print(e)
    #     return False
    # except Exception as e:  # some other error occured
        # logger.error(
        #     "{}:{}: other error occurred looking up {} in LDAP: {}".format(__file__, sys._getframe().f_code.co_name,
        #                                                                    uid, e))
        # print(e)
        # return False
    # shouldn't get here, but if we do, we don't have any results!
    # return False


if __name__ == "__main__":
    user = ldap_auth('', '')
    print(user)
