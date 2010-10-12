class Permission < ActiveRecord::Base
  belongs_to :User;
  belongs_to :Domain;
  belongs_to :Role;
  
  
  def <=>(x)
    self.role_id <=> x.role_id
  end
end