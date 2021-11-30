from django_auth_ldap.backend import LDAPBackend

ldapobj = LDAPBackend()
user = ldapobj.populate_user('')
user.is_anonymous()