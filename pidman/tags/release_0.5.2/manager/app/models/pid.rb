class Pid < ActiveRecord::Base
  
  belongs_to :domain
  belongs_to :ext_system
  belongs_to :creator, :class_name => 'User', :foreign_key => 'creator_id'
  belongs_to :editor, :class_name => 'User', :foreign_key => 'modified_by' 
  has_many   :PidHistory, :foreign_key => 'pid_id', :order => 'updated_at DESC'

  
  validates_associated :domain
  validates_associated :creator
    
  
  def self.find_by_uri_and_qualifier(uri, qualify)
    #self.find_by_sql("SELECT pid.id FROM pids as pid JOIN targets ON pid.id = targets.pid_id WHERE targets.uri = '#{uri}' AND targets.qualify = '#{qualify}'")
    
    find(:first, 
      :joins => "JOIN targets ON pids.id = targets.pid_id",
      :conditions => ["targets.uri = ? AND targets.qualify = ?", uri, qualify])
    
  end
  
  def self.find_by_target_and_qualify(uri, qualify)
    find(:all, 
         :joins => 'JOIN targets on pids.pid = targets.pid', 
         :conditions => ['targets.uri = ? AND targets.qualify = ?', uri, qualify])
    
  end  
end
