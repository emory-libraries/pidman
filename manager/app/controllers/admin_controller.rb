class AdminController < ApplicationController
before_filter :authenticate #require authentication
  def index
    render :action => "admin"
  end
end