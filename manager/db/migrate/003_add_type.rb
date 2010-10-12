class AddType < ActiveRecord::Migration
  def self.up
    add_column :pids, :type, :string, :limit => 25, :null => true, :default => 'Purl' 
  end

  def self.down
    remove_column :pids, :type
  end
end
