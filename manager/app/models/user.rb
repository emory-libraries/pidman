class User < ActiveRecord::Base
  has_many :Permissions
  has_many :Domains, :through => "permissions"
  has_many :Roles, :through => "permissions"
  #has_and_belongs_to_many :Roles, :join_table => 'domains_users'        

 #validates(:password, password_isValid(self.confirm)) 
  validates_presence_of(:username)

  # def self.admins_users(admin_id, is_superuser)
  # int admin_id
  # boolean is_superuser
  # collection of users admined by admin_id
  def self.admins_users(admin_id, is_superuser)
    unless(is_superuser)
      #select all users within admins domain
      self.find_by_sql("select * FROM users JOIN domains_users ON domains_users.user_id = users.id JOIN domains_users AS admin ON admin.domain_id = domains_users.domain_id WHERE admin.user_id = #{admin_id} and users.id != admin.user_id")  
    else
      #select all users except admin can not edit own record
      self.find_by_sql("select * FROM users WHERE id != #{admin_id}") 
    end
  end

  # def testRole(domain_id, role_id = nil)
  # string domain_id
  # string role_id default nil
  # return boolean
  # Test to see if user has specified role for domain
  def testRole(domain_id, role_id = nil)
    rv = false
    
    if (is_superuser)
      rv = true
    else
      self.Domains.each do | domain |
        if (domain.domain_id.to_i == domain_id && (role_id.nil? || domain.role_id.to_i == role_id))            
          rv = true
        end  
      end
    end
        
    return rv    
  end
  
  # def password_isValid(confirm)
  # string confirm user confirmed password
  # return boolean false if not valid
  # test to see if password is valid and = confirm 
  def password_isValid(confirm)
     if (self.password == confirm)
        return true
        #self.password =~ /^(?=.*d)(?=.*[a-z])(?=.*[A-Z])(?!.*s).{8,15}$/
        #for now do nothing
     else 
	return false
     end 
  end
   
  def setPermissions(permissions)
    permissions.each do |domain_id, role_id|
    
      p = Permission.new
        p.role_id   = role_id
        p.domain_id = domain_id
        p.user_id = self.id
      
      self.Permissions << p    
    
    end
  end   
  
  def dflt_role
    if (is_superuser)
      return 4
    else
      unless self.Permissions.nil?
        return self.Permissions.max.role_id
      else
        return 0
      end
    end
  end 
   
  def name
    return self.first + " " + self.last
  end
   
 end
