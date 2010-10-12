class ExtSystemAdminController < ApplicationController
before_filter :authenticate #require authentication
  def index
    list
    render :action => 'list'
  end

  # GETs should be safe (see http://www.w3.org/2001/tag/doc/whenToUseGet.html)
  verify :method => :post, :only => [ :destroy, :create, :update ],
         :redirect_to => { :action => :list }

  def list
    @ext_system_pages, @ext_systems = paginate :ext_systems, :per_page => 10
  end

  def show
    @ext_system = ExtSystem.find(params[:id])
  end

  def new
    @ext_system = ExtSystem.new
  end

  def create
    @ext_system = ExtSystem.new(params[:ext_system])
    if @ext_system.save
      flash[:notice] = 'ExtSystem was successfully created.'
      redirect_to :action => 'index', :controller => 'admin'
    else
      render :action => 'new'
    end
  end

  def edit
    @ext_system = ExtSystem.find(params[:id])
  end

  def update
    @ext_system = ExtSystem.find(params[:id])
    if @ext_system.update_attributes(params[:ext_system])
      flash[:notice] = 'ExtSystem was successfully updated.'
      redirect_to :action => 'index', :controller => 'admin'
    else
      render :action => 'edit'
    end
  end

  def destroy
    ExtSystem.find(params[:id]).destroy
    redirect_to :action => 'list'
  end
end
