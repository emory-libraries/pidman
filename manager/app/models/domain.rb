class Domain < ActiveRecord::Base
  has_and_belongs_to_many :Users
  has_and_belongs_to_many :Roles, :join_table => 'domains_users'  

  validates_presence_of :name
  
  def self.getDomainsForAdmin(admin_id, is_superuser)
  
    unless (is_superuser)
      @domains = find(:all, 
                    :select => 'domains.name, domains.id', 
                    :order => 'name', 
                    :joins => 'LEFT JOIN domains_users AS du ON du.domain_id = domains.id LEFT JOIN users AS u ON du.user_id = u.id',
                    :conditions => "du.user_id = #{admin_id}")
    else
      @domains = find(:all, :select => 'domains.name, domains.id')
    end 
    
    d = []    
    for domain in @domains
      d << [domain.name , domain.id]
    end  
    
    return d    
  end
end
