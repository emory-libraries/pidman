class PersisApiController < ApplicationController
  wsdl_service_name 'Persistent Identifier'
  web_service_api PersisApi
  web_service_scaffold :invoke
  before_invocation :invocation_authenticate,
                    :except => [:invoke,
                                :invoke_method_params,
                                :invoke_submit,
                                :invocation_authenticate] 
  before_invocation :verify_domain, :only => [:generateArk, :generatePurl]

  def generateArk
    u = User.find_by_username(params[:username])
    
    if u.nil?
      return "User not found"
    else
    
      unless (params[:external_system].nil? || params[:external_system] == '')
        ext_sys = ExtSystem.find_by_name(params[:external_system])
        ext_system_id  = ext_sys.id
        ext_system_key = params[:external_system_key] 
      else
        ext_system_id  = nil
        ext_system_key = nil
      end     
    
      if (u.testRole(params[:domain_id]))
        ark = Ark.generate(
          :user       => u,
          :domain_id  => params[:domain_id],
          :name       => params[:name], 
          :uri        => params[:uri],
          :qualifier  => params[:qualifier],
          :proxy_id   => params[:proxy_id],
          :ext_system => params[:external_system],
          :ext_key    => params[:external_system_key]
        )
        
        return ark.targets[0].getURL
      else
        RAILS_DEFAULT_LOGGER.error("not authorized")
        return "Not Authorized"
      end
    end

  end

  def generatePurl
    u = User.find_by_username(params[:username])
    
    if u.nil?
      return "User not found"
    else

      unless (params[:external_system].nil? || params[:external_system] == '')
        ext_sys = ExtSystem.find_by_name(params[:external_system])
        ext_system_id  = ext_sys.id
        ext_system_key = params[:external_system_key] 
      else
        ext_system_id  = nil
        ext_system_key = nil
      end    
    
      if (u.testRole(params[:domain_id]))
        purl = Purl.generate(
          :user           => u,
          :domain_id      => params[:domain_id],
          :name           => params[:name], 
          :uri            => params[:uri],
          :proxy_id       => params[:proxy_id],
          :ext_system_id  => ext_system_id,
          :ext_system_key => ext_system_key          
        )
        
        return purl.targets[0].getURL
      else
        RAILS_DEFAULT_LOGGER.error("not authorized")
        return "Not Authorized"        
      end
   end 
  end
  
  def addArkTarget    
    params[:pid] = params[:noid]
    
    ark = Ark.find_by_pid(params[:pid])
    return ark.addTarget(params).getURL
  end
  
  def editTarget
    t = Target.find_by_purl(params[:purl])
    t.update_attribute(:uri, params[:uri])
    return t.getURL
  end
  
  def listDomains
    u = User.find_by_username(params[:username])
  
    return Domain.find_by_user_id(u.id)
  end
  
  protected
     def invocation_authenticate(x, y) #params are not used but will not compile without
      #test for username, password
      u = User.find_by_username_and_password(params[:username], Digest::MD5.hexdigest(params[:password]))
      if (u.nil?)
        return [false, "not authorized"] 
      end            
      return true
    end
    
    def verify_domain(x,y) #params are not used but will not compile without
      #test for valid domain
      begin
        d = Domain.find(params[:domain_id])
      ensure        
        return [false, "invalid domain_id"] if (d.nil?)
      end
    end
end
