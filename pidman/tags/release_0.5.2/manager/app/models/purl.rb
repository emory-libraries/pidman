class Purl < Pid
  #actually will only have one has many will create an array for consistancy with ark
  has_many  :targets, :class_name => 'Target', :foreign_key => 'pid_id',
            :conditions => "qualify IS NULL", :dependent => :destroy          
  belongs_to :domain
  belongs_to :ext_system
             
  validates_associated :targets
  validates_associated :domain
    
  def self.generate(options)

    purl = Purl.new
      purl.pid             = ActiveRecord::Base::DBFunction.new(:mint_noid, NOID_PATH) 
      purl.created_at      = Time::now
      purl.creator_id      = options[:user].id
      purl.modified_by     = options[:user].id
      purl.name            = options[:name]
      purl.domain_id       = options[:domain_id]
      
      purl.ext_system_id   = options[:ext_system_id]
      purl.ext_system_key  = options[:ext_system_key]

    purl.save

    #get data from fresh purl -- pid is not minted until save 
    purl = Purl.find(purl.id)
      
    t          = Target.new
      t.pid      = purl.pid
      t.uri      = options[:uri]
      t.qualify  = nil
      t.proxy_id = options[:proxy_id]
     
    purl.targets << t  
      
    RAILS_DEFAULT_LOGGER.debug(ID_SERVER_URL + purl.pid)      
    return purl
  end    
    
  def getTargetURL(id)
      return ID_SERVER_URL + '/' + self.pid    
  end    

end
