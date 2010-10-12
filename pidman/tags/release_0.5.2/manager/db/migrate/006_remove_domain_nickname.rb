class RemoveDomainNickname < ActiveRecord::Migration
  def self.up
    remove_column :domains, :nickname
  end

  def self.down
    add_column :domains, :nickname, :string, :limit=>20
  end
end
