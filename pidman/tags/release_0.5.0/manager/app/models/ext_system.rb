class ExtSystem < ActiveRecord::Base
  validates_presence_of(:name)
  validates_presence_of(:key_field)
end
