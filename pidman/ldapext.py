from eulcore.ldap.auth.backends import LDAPBackend

class PidmanLDAPBackend(LDAPBackend):
    def create_user(self, username):
        user = super(PidmanLDAPBackend, self).create_user(username)
        user.is_staff = True
        return user
