class PersisController < ApplicationController
  before_filter :authenticate #require authentication

  def index
    list
    render :action => 'list'
  end

  # GETs should be safe (see http://www.w3.org/2001/tag/doc/whenToUseGet.html)
  verify :method => :post, :only => [ :destroy, :create, :update ],
         :redirect_to => { :action => :list }

  def list
#  @cogs = Cog.find(:all,
# :page => {:size => 10,
# :current => params[:page]})    
    
    
    if (params[:sort].nil?)      
      @direction = 'ASC'       
      sort = 'name' + ' ' + @direction     
    else
      sort = params[:sort] + ' ' + params[:direction]
      @direction = (params[:direction] == 'ASC') ? 'DESC' : 'ASC'
    end
  
    @Pids = Pid.find(:all, :order => sort, :page => {:size => 50, :current => params[:page]})        
    
  end

  def auto_complete_search
    doSearch(params[:search])
      
    render :partial => 'auto_complete_search'
  end

  def doSearch(value)
    searchTerm = value.downcase
    
    conditions = Array.new
    conditions << "LOWER(name)   LIKE '%#{searchTerm}%'"
  
    @pids = Pid.find(:all, 
      :conditions => conditions.join(' OR '), 
      :order => 'updated_at DESC')  
  end 

  def search 
    doSearch(params[:search])
    render :action => 'list'      
  end

  def show
    #@pids = Pid.find_by_pid(params[:pid]) unless params[:pid].nil?
    @pids = Pid.find(params[:id])
  end

  def new
    if (params[:type] == 'Purl')
      @pids = Purl.new
    else
      @pids = Ark.new
    end
  end
  
  def createArk
    @pids = Ark.generate(
      :user       =>  session[:active_user], 
      :domain_id  =>  params[:pids][:domain_id], 
      :name       =>  params[:pids][:name], 
      :uri        =>  params[:target][:uri], 
      :qualifier  =>  params[:target][:qualifier],
      :proxy_id   =>  params[:target][:proxy_id]
    )
    
    flash[:notice] = "Ark created. " + @pids.targets[0].getURL
    redirect_to :action => 'list'    
  end

  def createPurl
    @pids = Purl.generate(
      :user       =>  session[:active_user], 
      :domain_id  =>  params[:pids][:domain_id], 
      :name       =>  params[:pids][:name], 
      :uri        =>  params[:target][:uri],
      :proxy_id   =>  params[:target][:proxy_id]      
    )
    
    flash[:notice] = "Purl created. " + @pids.targets[0].getURL
    redirect_to :action => 'list'
  end
  
  def edit
    @pids = Pid.find(params[:id])
  end
  
  def update    
    @pids = Pid.find(params[:id])  
    @pids.modified_by = session[:active_user][:id]
    
    @pids.addTarget(params[:target]) if (@pids.class == Ark && params[:commit] == 'Add Target')
    
    if @pids.update_attributes(params[:pids])
      flash[:notice] = "#{@pids.class} was successfully updated."
    end 
      
    render :action => 'edit'
  end

  def destroy
    Pid.find(params[:id]).destroy
    redirect_to :action => 'list'
  end  
  
  def pid_history
    @pidHistory = PidHistory.find(:all, :conditions => 'pid = ' + params[:pid], :order => 'created_at DESC')
  end
end
