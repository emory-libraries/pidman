class Authenticate    

    def self.login(username, password, session)
    
      pwd = Digest::MD5.hexdigest(password)
      u = User.find_by_username_and_password(username, pwd)   
      
      unless (u.nil?)
        RAILS_DEFAULT_LOGGER.error "Authenticate::login  Authenticated setting session"
        session[:active_user] = u
        session[:active_user][:dflt_role] = u.dflt_role
        session[:login] = true
        return true
      else
        RAILS_DEFAULT_LOGGER.error "Authenticate::login  Not Authenticated clearing session"
        session[:active_user] = nil
        session[:login] = nil        
        return false
      end      
    end
end