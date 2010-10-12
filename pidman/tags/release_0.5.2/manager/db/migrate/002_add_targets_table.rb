class AddTargetsTable < ActiveRecord::Migration
  def self.up
    create_table "targets", :force => true do |t|
      t.column "pid_id", :integer
      t.column "pid", :string
      t.column "uri", :string, :limit => 2048, :null => false  
      t.column "qualify", :string, :limit => 255, :null => true
    end  
  
    create_table "archive_targets", :force => true do |t|
      t.column "pid_id", :integer
      t.column "pid", :string
      t.column "uri", :string, :limit => 2048, :null => false  
      t.column "qualify", :string, :limit => 255, :null => true
    end
    
    Pid.find(:all).each do |p|
      t = Target.new
        t.pid_id    = p.id
        t.pid       = p.pid
        t.uri    = p.target
        t.qualify   = nil
      t.save
    end
        
    execute "ALTER TABLE archive_targets ADD COLUMN sort_order serial"  
    remove_column :pids, :target
    
    print "TO COMPLETE STEP PLEASE RUN add_triggers_and_functions.sql AS POSTGRES SUPERUSER\n"
  end

  def self.down
    add_column :pids, :target, :string, :limit => 2048, :null => true
  
    Target.find(:all).each do |t|
      p = Pid.find(t.pid_id)
        p.target = t.uri
      p.save
    end

    change_column :pids, :target, :string, :null => false
  
    drop_table :targets
    drop_table :archive_targets
    
 end
end
