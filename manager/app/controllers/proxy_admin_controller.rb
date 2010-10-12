class ProxyAdminController < ApplicationController
before_filter :authenticate #require authentication
  def index
    list
    render :action => 'list'
  end

  # GETs should be safe (see http://www.w3.org/2001/tag/doc/whenToUseGet.html)
  verify :method => :post, :only => [ :destroy, :create, :update ],
         :redirect_to => { :action => :list }

  def list
    @proxy_pages, @proxies = paginate :proxies, :per_page => 10
  end

  def show
    @proxy = Proxy.find(params[:id])
  end

  def new
    @proxy = Proxy.new
  end

  def create
    @proxy = Proxy.new(params[:proxy])
    if @proxy.save
      flash[:notice] = 'Proxy was successfully created.'
      redirect_to :action => 'index', :controller => 'admin'
    else
      render :action => 'new'
    end
  end

  def edit
    @proxy = Proxy.find(params[:id])
  end

  def update
    @proxy = Proxy.find(params[:id])
    if @proxy.update_attributes(params[:proxy])
      flash[:notice] = 'Proxy was successfully updated.'
      redirect_to :action => 'index', :controller => 'admin'
    else
      render :action => 'edit'
    end
  end

  def destroy
    Proxy.find(params[:id]).destroy
    redirect_to :action => 'list'
  end
end
