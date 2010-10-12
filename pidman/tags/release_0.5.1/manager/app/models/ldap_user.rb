
class LdapUser #< ActiveLDAP::Base

#    ldap_mapping :prefix => "cn=users" 
#    
#    def self.login(username, password)
#      begin
#        ActiveLDAP::Base.connect(
#          :host => "ldap-auth.service.emory.edu",
#          :port => 636,
#          :base => "o=emory.edu",
#         :bind_format => "uid=#{username},ou=people,o=emory.edu",
#          :password_block => Proc.new { password },
#          :allow_anonymous => false
#        )
#        ActiveLDAP::Base.close
#        return true
#      rescue ActiveLDAP::AuthenticationError
#        return false
#      end
#    end
    

end
