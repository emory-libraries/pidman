class MakeKeysBigger < ActiveRecord::Migration
  def self.up
   
    add_column :pids, :tmp_id, :bigint
    
    Pid.find(:all).each do |p|
      p.tmp_id = p.id
    end
    
    remove_column :pids, :id
    add_column :pids, :id, :bigserial

    Pid.find(:all).each do |p|
      p.id = p.tmp_id
    end    
    remove_column :pids, :tmp_id
    
    #archive_pids
    add_column :archive_pids, :tmp_id, :bigint
    
    PidHistory.find(:all).each do |p|
      p.tmp_id = p.id
    end
    
    remove_column :archive_pids, :id
    add_column :archive_pids, :id, :bigserial

    PidHistory.find(:all).each do |p|
      p.id = p.tmp_id
    end        
    remove_column :archive_pids, :tmp_id
    
    #targets
    add_column :targets, :tmp_id, :bigint
    
    Target.find(:all).each do |p|
      p.tmp_id = p.id
    end
    
    remove_column :targets, :id
    add_column :targets, :id, :bigserial

    Target.find(:all).each do |p|
      p.id = p.tmp_id
    end  
    remove_column :targets, :tmp_id
    
    #archive_targets
    add_column :archive_targets, :tmp_id, :bigint
    
    TargetHistory.find(:all).each do |p|
      p.tmp_id = p.id
    end
    
    remove_column :archive_targets, :id
    add_column :archive_targets, :id, :bigserial

    TargetHistory.find(:all).each do |p|
      p.id = p.tmp_id
    end      
    remove_column :archive_targets, :tmp_id
  end

  def self.down
    #pids
    add_column :pids, :tmp_id, :integer
    
    Pid.find(:all).each do |p|
      p.tmp_id = p.id
    end
    
    remove_column :pids, :id
    add_column :pids, :id, :integer

    Pid.find(:all).each do |p|
      p.id = p.tmp_id
    end
    remove_column :pids, :tmp_id
    
    #archive_pids
    add_column :archive_pids, :tmp_id, :integer
    
    PidHistory.find(:all).each do |p|
      p.tmp_id = p.id
    end
    
    remove_column :archive_pids, :id
    add_column :archive_pids, :id, :integer

    PidHistory.find(:all).each do |p|
      p.id = p.tmp_id
    end 
    remove_column :archive_pids, :tmp_id

    #targets
    add_column :targets, :tmp_id, :integer
    
    Target.find(:all).each do |p|
      p.tmp_id = p.id
    end
    
    remove_column :targets, :id
    add_column :targets, :id, :integer

    Target.find(:all).each do |p|
      p.id = p.tmp_id
    end 
    remove_column :targets, :tmp_id
    
    #archive_targets
    add_column :archive_targets, :tmp_id, :integer
    
    TargetHistory.find(:all).each do |p|
      p.tmp_id = p.id
    end
    
    remove_column :archive_targets, :id
    add_column :archive_targets, :id, :integer

    TargetHistory.find(:all).each do |p|
      p.id = p.tmp_id
    end       
    remove_column :archive_targets, :tmp_id
  end
end
