require File.dirname(__FILE__) + '/../test_helper'
require 'persis_controller'

# Re-raise errors caught by the controller.
class PersisController; def rescue_action(e) raise e end; end

class PersisControllerTest < Test::Unit::TestCase
  fixtures :pids, :targets, :users

  def setup
    @controller = PersisController.new
    @request    = ActionController::TestRequest.new
    @response   = ActionController::TestResponse.new
  end
  
  def test_truth
    assert true
  end  

  def test_createArk
    loginUser users(:first)

    n = Ark.find(:all).size
    get :createArk, :pids => ark_opts, :target => target_opts
    
    assert_response :redirect
    assert_redirected_to :action => 'list'
    
    assert_equal n +1, Ark.find(:all).size

    
  end
  
  
  def ark_opts(options = {})
    {
    :domain_id => 1,
    :name => 'The NY Times',
    }.merge(options)
  end
  
  def target_opts(options = {})
    {
    :uri => 'http://www.nytimes.com',
    :qualifier => '??',
    :proxy_id => nil
    }.merge(options)
  end  

end
