class Target < ActiveRecord::Base  
  belongs_to :Pid
  belongs_to :proxy
  
  validates_associated :proxy

  before_save :clean_target, :replace_token
  
  def getURL
    return self.Pid.getTargetURL(self.id)
  end
  
  def self.find_by_purl(purl)
    uri = URI::parse(purl)
    fragments = uri.path.split('/')
    
    if (uri.path.starts_with?("/ark:/#{EMORY_ARK_NAAN}/"))
      n = fragments[3]
      q = fragments[4]
    else
      n = fragments[1]
      q = nil
    end
    
    return self.find_by_pid_and_qualify(n, p)
  end
  
protected
  def clean_target
    self.qualify = (self.qualify && self.qualify.strip == '') ? nil : self.qualify 
    self.proxy_id = nil if (self.proxy_id == 0)
    return true
  end
  
  def replace_token
    self.uri.gsub!('{%PID%}',self.pid)
    return true
  end
end
