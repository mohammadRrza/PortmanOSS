import ldap

LDAP_SERVER = 'ldap://172.28.238.238:389'
LDAP_BASE = "DC=pishgaman,DC=local"


def ldap_auth(username, password):
    conn = ldap.initialize(LDAP_SERVER)
    try:
        conn.protocol_version = ldap.VERSION3
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.simple_bind_s(username, password)
        logon_name = conn.whoami_s().split('\\')[1]
        search_filter = f"(sAMAccountName={logon_name})"
        retrieve_attributes = ['memberOf', 'cn']
        search_res = conn.search_s(LDAP_BASE, ldap.SCOPE_SUBTREE, search_filter, retrieve_attributes)
        result_obj = search_res[0][1]
        if isinstance(result_obj, dict):
            fullname = result_obj.get('cn')[0].decode('utf-8')
            group_info = [value.decode('utf-8') for value in result_obj.get('memberOf')]
        group_name = [gp.split(",")[0].split("=")[1] for gp in group_info]

    except ldap.LDAPError as e:
        return dict(message="Failed to authenticate")

    conn.unbind_s()
    return dict(message="Success", fullname=fullname, group_name=group_name, logon_name=logon_name)


if __name__ == "__main__":
    user = ldap_auth('0422094080@pishgaman.local', 'Nahid_1414')
    print(user)
