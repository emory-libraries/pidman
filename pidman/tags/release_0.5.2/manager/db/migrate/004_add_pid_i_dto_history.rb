class AddPidIDtoHistory < ActiveRecord::Migration
  def self.up
    add_column :archive_pids, :pid_id, :integer, :null => true
  end

  def self.down
    remove_column :archive_pids, :pid_id
  end
end
