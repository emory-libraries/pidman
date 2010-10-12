class ProxyTarget < ActiveRecord::Migration
  def self.up
    add_column :targets, :proxy_id, :integer, :null => true
    add_column :archive_targets, :proxy_id, :integer, :null => true, :default => nil

    execute "CREATE OR REPLACE FUNCTION \"archive_pids\" () RETURNS \"trigger\" AS 
      'BEGIN
        INSERT INTO archive_pids (pid_id, pid, domain_id, active, name, last_modified, ext_system_id, ext_system_key, creator_id, created_at, modified_by) VALUES (
          OLD.id,
          OLD.pid,
          OLD.domain_id,
          OLD.active,
          OLD.name,
          OLD.last_modified,
          OLD.ext_system_id,
          OLD.ext_system_key,
          OLD.creator_id,
          OLD.created_at,
          OLD.modified_by
        ) ;
      RETURN NULL ;
      END ;' 
      
      LANGUAGE \"plpgsql\"
      VOLATILE
      RETURNS NULL ON NULL INPUT
      SECURITY INVOKER"    

    execute "CREATE OR REPLACE FUNCTION \"archive_targets\" () RETURNS \"trigger\" AS 
      'BEGIN
        INSERT INTO archive_targets (pid_id, pid, uri, qualify, proxy_id) VALUES (
          OLD.pid_id,
          OLD.pid,
          OLD.uri,
          OLD.qualify,
          OLD.proxy_id
        ) ;
        RETURN NULL ;
      END ;'       
      LANGUAGE \"plpgsql\"
      VOLATILE
      RETURNS NULL ON NULL INPUT
      SECURITY INVOKER"      
    
    
    remove_column :pids, :proxy_id
    remove_column :archive_pids, :proxy_id
  end

  def self.down
    add_column :pids, :proxy_id, :integer, :null => true
    add_column :archive_pids, :proxy_id, :integer, :null => true, :default => nil

    execute "CREATE OR REPLACE FUNCTION \"archive_pids\" () RETURNS \"trigger\" AS 
      'BEGIN
        INSERT INTO archive_pids (pid_id, pid, proxy_id, domain_id, active, name, last_modified, ext_system_id, ext_system_key, creator_id, created_at, modified_by) VALUES (
          OLD.id,
          OLD.pid,
          OLD.proxy_id,
          OLD.domain_id,
          OLD.active,
          OLD.name,
          OLD.last_modified,
          OLD.ext_system_id,
          OLD.ext_system_key,
          OLD.creator_id,
          OLD.created_at,
          OLD.modified_by
        ) ;
      RETURN NULL ;
      END ;' 
      
      LANGUAGE \"plpgsql\"
      VOLATILE
      RETURNS NULL ON NULL INPUT
      SECURITY INVOKER"

    execute "CREATE OR REPLACE FUNCTION \"archive_targets\" () RETURNS \"trigger\" AS 
      'BEGIN
        INSERT INTO archive_targets (pid_id, pid, uri, qualify) VALUES (
          OLD.pid_id,
          OLD.pid,
          OLD.uri,
          OLD.qualify
        ) ;
        RETURN NULL ;
      END ;'       
      LANGUAGE \"plpgsql\"
      VOLATILE
      RETURNS NULL ON NULL INPUT
      SECURITY INVOKER"     

    remove_column :targets, :proxy_id
    remove_column :archive_targets, :proxy_id    
  end
end
