class Ark < Pid
  has_many   :targets, :class_name => 'Target', :foreign_key => 'pid_id', :dependent => :destroy
  belongs_to :domain
  belongs_to :ext_sytem

  def self.generate(options)
    ark = Ark.new
      ark.pid             = ActiveRecord::Base::DBFunction.new(:mint_noid, NOID_PATH) 
      ark.created_at      = Time::now
      ark.creator_id      = options[:user].id
      ark.modified_by     = options[:user].id
      ark.name            = options[:name]
      ark.domain_id       = options[:domain_id]
      
      ark.ext_system_id   = options[:ext_system_id]
      ark.ext_system_key  = options[:ext_system_key]
    ark.save

    #get data from fresh ark -- pid is not minted until save 
    ark.reload()
    ark.addTarget(options)  
     
    return ark
  end
  
  def addTarget(values)
    t = Target.create({:pid => self.pid, :pid_id => self.id, :uri => values[:uri], :qualify => values[:qualifier], :proxy_id => values[:proxy_id]})
    self.targets << t  
    
    return t
  end

  def self.update(u, pid, name, uri, q)
    ark = Ark.find_by_pid(pid)
      ark.modified_by     = u.id
      ark.name            = name
    ark.save
     
    t = Target.find_by_pid_and_qualify(pid,q) || Target.new
      t.pid      = pid
      t.uri      = uri
      t.qualify  = q
    t.save

    #get data from fresh ark -- pid is not minted until save 
    ark.reload()

    return ark    
  end

  def getTargetURL(id)
      t = Target.find(id)
      q = (t.qualify.nil?) ? '' : '/' + t.qualify
      
      return ID_SERVER_URL + "/ark:/" + EMORY_ARK_NAAN + "/" + self.pid + q    
  end

end
