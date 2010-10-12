require File.dirname(__FILE__) + '/../test_helper'
require 'proxy_admin_controller'

# Re-raise errors caught by the controller.
class ProxyAdminController; def rescue_action(e) raise e end; end

class ProxyAdminControllerTest < Test::Unit::TestCase
  fixtures :proxies

  def setup
    @controller = ProxyAdminController.new
    @request    = ActionController::TestRequest.new
    @response   = ActionController::TestResponse.new
  end

  def test_truth
    assert true
  end

#  def test_index
#    get :index
#    assert_response :success
#    assert_template 'list'
#  end
#
#  def test_list
#    get :list
#
#    assert_response :success
#    assert_template 'list'
#
#    assert_not_nil assigns(:proxies)
#  end
#
#  def test_show
#    get :show, :id => 1
#
#    assert_response :success
#    assert_template 'show'
#
#    assert_not_nil assigns(:proxy)
#    assert assigns(:proxy).valid?
#  end
#
#  def test_new
#    get :new
#
#    assert_response :success
#    assert_template 'new'
#
#    assert_not_nil assigns(:proxy)
#  end
#
#  def test_create
#    num_proxies = Proxy.count
#
#    post :create, :proxy => {}
#
#    assert_response :redirect
#    assert_redirected_to :action => 'list'
#
#    assert_equal num_proxies + 1, Proxy.count
#  end
#
#  def test_edit
#    get :edit, :id => 1
#
#    assert_response :success
#    assert_template 'edit'
#
#    assert_not_nil assigns(:proxy)
#    assert assigns(:proxy).valid?
#  end
#
#  def test_update
#    post :update, :id => 1
#    assert_response :redirect
#    assert_redirected_to :action => 'show', :id => 1
#  end
#
#  def test_destroy
#    assert_not_nil Proxy.find(1)
#
#    post :destroy, :id => 1
#    assert_response :redirect
#    assert_redirected_to :action => 'list'
#
#    assert_raise(ActiveRecord::RecordNotFound) {
#      Proxy.find(1)
#    }
#  end
end
