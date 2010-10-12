module AuthenticateTestHelper
  

  def loginUser(u)
    @request.session[:active_user] = u
    @request.session[:login]       = true
    @request.session[:active_user][:dflt_role] = 2
  end
end