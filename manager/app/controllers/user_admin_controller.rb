class UserAdminController < ApplicationController
before_filter :authenticate   #require authentication 
  
  def index
    list
    render :action => 'list'
  end

  # GETs should be safe (see http://www.w3.org/2001/tag/doc/whenToUseGet.html)
  verify :method => :post, :only => [ :destroy, :create, :update ],
         :redirect_to => { :action => :list }

  def list
    #@user_pages, @users = paginate :users, :per_page => 10
    @users = User.admins_users(session[:active_user][:id], session[:active_user][:is_superuser])
  end

  def show
    @user = User.find(params[:id])
  end

  def new
    @user = User.new
  end

  def create
    @user = User.new(params[:user])
    @user.password = Digest::MD5.hexdigest(params[:user][:password])

    unless (params[:user][:is_superuser] == "true")
      @user.setPermissions(params[:u][:permission])    
    end     
    
    if @user.save
      flash[:notice] = 'User was successfully created.'
      redirect_to :action => 'index', :controller => 'admin'
    else
      redirect_to :action => 'new'
    end
  end

  def edit
    @user = User.find(params[:id])
  end

  def editProfile
    redirect_to :action => 'edit', :id => session[:active_user][:id]
  end

  def update
    @user = User.find(params[:id])
    @user.password = Digest::MD5.hexdigest(params[:user][:password])
    
    unless (params[:user][:is_superuser] == "true")
      @user.setPermissions(params[:u][:domain_role])    
    end 
    
    if @user.update_attributes(params[:user])
      flash[:notice] = 'User was successfully updated.'
      redirect_to :action => 'index', :controller => 'admin'
    else
      render :action => 'edit'
    end
  end

  def destroy
    User.find(params[:id]).destroy
    redirect_to :action => 'list'
  end
  
  private

end
