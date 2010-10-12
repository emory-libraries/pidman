# Filters added to this controller will be run for all controllers in the application.
# Likewise, all the methods added will be available for all controllers.
class ApplicationController < ActionController::Base

  #filter logs
  filter_parameter_logging :password, :password_confirmation

  protected
    def authenticate
      unless session[:login]
        @session[:return_to] = @request.request_uri
        redirect_to :controller => "login", :action => "index"
        return false
      else
        return true
      end
  end
end
