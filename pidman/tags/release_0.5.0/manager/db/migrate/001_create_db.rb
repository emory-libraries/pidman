class CreateDb < ActiveRecord::Migration
  def self.up
    create_table "archive_pids", :force => true do |t|
      t.column "pid", :string
      t.column "target", :string, :limit => 2048, :null => false
      t.column "proxy_id", :integer, :default => 0, :null => false
      t.column "domain_id", :integer, :null => false
      t.column "active", :boolean
      t.column "name", :string, :limit => 1023
      t.column "last_modified", :datetime, :null => false
      t.column "ext_system_id", :integer
      t.column "ext_system_key", :string, :limit => 1023
      t.column "creator_id", :integer, :null => false
      t.column "created_at", :datetime, :null => false
      t.column "modified_by", :integer, :null => false
    end
  
    create_table "domains", :force => true do |t|
      t.column "name", :string, :null => false
      t.column "last_modified", :datetime, :null => false
    end
  
    add_index "domains", ["name"], :name => "domains_name_key", :unique => true
  
    create_table "permissions", :force => true do |t|
      t.column "user_id", :integer, :null => false
      t.column "domain_id", :integer, :null => false
      t.column "role_id", :integer, :null => false
      t.column "last_modified_at", :datetime, :null => false
    end
  
    create_table "ext_systems", :force => true do |t|
      t.column "name", :string, :limit => 127, :null => false
      t.column "key_field", :string, :limit => 127, :null => false
      t.column "last_modified", :datetime, :null => false
    end
  
    add_index "ext_systems", ["name"], :name => "ext_systems_name_key", :unique => true
  
    create_table "pids", :force => true do |t|
      t.column "pid", :string, :null => false
      t.column "target", :string, :limit => 2048, :null => false
      t.column "proxy_id", :integer, :default => 0, :null => false
      t.column "domain_id", :integer, :default => 0, :null => false
      t.column "active", :boolean, :default => true
      t.column "name", :string, :limit => 1023
      t.column "ext_system_id", :integer
      t.column "ext_system_key", :string, :limit => 1023
      t.column "creator_id", :integer, :null => false
      t.column "created_at", :datetime, :null => false
      t.column "last_modified", :datetime, :null => false
      t.column "modified_by", :integer, :null => false
    end
  
    add_index "pids", ["pid"], :name => "pid_index"
    add_index "pids", ["pid"], :name => "pids_pid_key", :unique => true
    add_index "pids", ["pid"], :name => "pids_pid_key1", :unique => true
    add_index "pids", ["target"], :name => "target_index"
  
    create_table "proxies", :force => true do |t|
      t.column "name", :string, :limit => 127, :null => false
      t.column "transform", :string, :limit => 127, :null => false
      t.column "last_modified", :datetime, :null => false
    end
  
    add_index "proxies", ["name"], :name => "proxies_name_key", :unique => true
  
    create_table "roles", :force => true do |t|
      t.column "role", :string, :limit => 64, :null => false
      t.column "last_modified", :datetime, :null => false
    end
  
    create_table "users", :force => true do |t|
      t.column "username", :string, :limit => 32
      t.column "first", :string, :limit => 127, :null => false
      t.column "last", :string, :limit => 127, :null => false
      t.column "email", :string, :limit => 320
      t.column "last_modified", :datetime, :null => false
      t.column "password", :string, :limit => 150
      t.column "is_superuser", :boolean, :default => false, :null => false
    end
  
    add_index "users", ["email"], :name => "users_email_key", :unique => true
    add_index "users", ["username"], :name => "users_username_key", :unique => true  
    
  end

  def self.down
    drop_table :archive_pids
    drop_table :domains
    drop_table :permissions
    drop_table :ext_systems
    drop_table :pids
    drop_table :proxies
    drop_table :roles
    drop_table :users
  end
end
