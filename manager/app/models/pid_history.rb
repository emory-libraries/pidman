class PidHistory < ActiveRecord::Base
  set_table_name "archive_pids" 
  
  belongs_to :proxy
  belongs_to :domain
  belongs_to :ext_system
  belongs_to :creator, :class_name => 'User', :foreign_key => 'creator_id' 
  belongs_to :editor,  :class_name => 'User', :foreign_key => 'modified_by' 
  has_many   :targets, :class_name => 'TargetHistory', :foreign_key => 'pid_id', :order => 'sort_order DESC'
end