class LoginController < ApplicationController
  def index
    render :action => "login" 
  end

  def login
    # the actual login process
    if @params[:login]
      @values = @params[:login]
      
      unless (Authenticate.login(@values[:un], @values[:pw], session))
        flash[:notice] = "Incorrect username and or password" 
      else
        unless (@session[:return_to])
          redirect_to :controller => "admin"
        else
          redirect_to @session[:return_to]   
        end
        return         
      end 
    end
    
    render :action => "login"
  end
  
  def logout()
    session[:login]       = nil
    session[:active_user] = nil    
    session[:return_to]   = nil
    redirect_to :controller => "admin"
  end
end
