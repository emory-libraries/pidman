class Modifiedat < ActiveRecord::Migration
  def self.up
    #archive_pids
    add_column :archive_pids, :updated_at, :datetime, :null => true
    PidHistory.find(:all).each do |t|
      t.modified_at = t.last_modified
      t.save
    end
    remove_column :archive_pids, :last_modified

    #domains
    add_column :domains, :updated_at, :datetime, :null => true
    Domain.find(:all).each do |t|
      t.updated_at = t.last_modified
      t.save
    end
    remove_column :domains, :last_modified
    
    #ext_systems
    add_column :ext_systems, :updated_at, :datetime, :null => true
    ExtSystem.find(:all).each do |t|
      t.updated_at = t.last_modified
      t.save
    end
    remove_column :ext_systems, :last_modified
    
    #pids
    add_column :pids, :updated_at, :datetime, :null => true
    Pid.find(:all).each do |t|
      t.updated_at = t.last_modified
      t.save
    end
    remove_column :pids, :last_modified
    
    #proxies
    add_column :proxies, :updated_at, :datetime, :null => true
    Proxy.find(:all).each do |t|
      t.updated_at = t.last_modified
      t.save
    end
    remove_column :proxies, :last_modified
    
    #roles
    add_column :roles, :updated_at, :datetime, :null => true
    Role.find(:all).each do |t|
      t.updated_at = t.last_modified
      t.save
    end
    remove_column :roles, :last_modified
    
    #users
    add_column :users, :updated_at, :datetime, :null => true
    User.find(:all).each do |t|
      t.updated_at = t.last_modified
      t.save
    end    
    remove_column :users, :last_modified
    
  end

  def self.down
    #archive_pids
    add_column :archive_pids, :last_modified, :datetime, :null => true
    PidHistory.find(:all).each do |t|
      t.last_modified = t.updated_at
      t.save
    end
    remove_column :archive_pids, :updated_at

    #domains
    add_column :domains, :last_modified, :datetime, :null => true
    Domain.find(:all).each do |t|
      t.last_modified = t.updated_at
      t.save
    end
    remove_column :domains, :updated_at
    
    #ext_systems
    add_column :ext_systems, :last_modified, :datetime, :null => true
    ExtSystem.find(:all).each do |t|
      t.last_modified = t.updated_at
      t.save
    end
    remove_column :ext_systems, :updated_at
    
    #pids
    add_column :pids, :last_modified, :datetime, :null => false
    Pid.find(:all).each do |t|
      t.last_modified = t.updated_at
      t.save
    end
    remove_column :pids, :updated_at
    
    #proxies
    add_column :proxies, :last_modified, :datetime, :null => true
    Proxy.find(:all).each do |t|
      t.last_modified = t.updated_at
      t.save
    end
    remove_column :proxies, :updated_at
    
    #roles
    add_column :roles, :last_modified, :datetime, :null => true
    Role.find(:all).each do |t|
      t.last_modified = t.updated_at
      t.save
    end
    remove_column :roles, :updated_at
    
    #users
    add_column :users, :last_modified, :datetime, :null => true
    User.find(:all).each do |t|
      t.last_modified = t.updated_at
      t.save
    end    
    remove_column :users, :updated_at    
  end
end
