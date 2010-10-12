class TargetsController < ApplicationController
  def index
    list
    render :action => 'list'
  end

  def show
    @target = Target.find(params[:id])
  end

  def new()
    @target = Target.new
    @target.Pid = Pid.find(params[:pid_id])
    @target.pid = @target.Pid.pid
  end

  def create
    @target = Target.new(params[:target])
    if @target.save
      flash[:notice] = 'Target was successfully created.'
      redirect_to :action => 'list', :controller => 'persis'
    else
      render :action => 'new'
    end
  end

  def edit
    @target = Target.find(params[:id])
  end

  def update
    @target = Target.find(params[:id])
    if @target.update_attributes(params[:target])
      flash[:notice] = 'Target was successfully updated.'
      redirect_to :action => 'edit', :controller => 'persis', :id => @target.pid_id
    else
      render :action => 'edit'
    end
  end

  def destroy
    t = Target.find(params[:id]).destroy
    redirect_to :action => 'edit', :controller => 'persis', :id => t.pid_id
  end
end
