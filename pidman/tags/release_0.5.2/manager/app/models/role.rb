class Role < ActiveRecord::Base
  has_and_belongs_to_many :Users,   :join_table => 'domains_users'  
  has_and_belongs_to_many :Roles,   :join_table => 'domains_users'
  has_and_belongs_to_many :Domains, :join_table => 'domains_users'
  
  
  def self.displayRole(role_id)
    r = Role.find(role_id)
    return r.role
  end
end
