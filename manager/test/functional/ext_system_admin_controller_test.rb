require File.dirname(__FILE__) + '/../test_helper'
require 'ext_system_admin_controller'

# Re-raise errors caught by the controller.
class ExtSystemAdminController; def rescue_action(e) raise e end; end

class ExtSystemAdminControllerTest < Test::Unit::TestCase
  fixtures :ext_systems

  def setup
    @controller = ExtSystemAdminController.new
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
#    assert_not_nil assigns(:ext_systems)
#  end
#
#  def test_show
#    get :show, :id => 1
#
#    assert_response :success
#    assert_template 'show'
#
#    assert_not_nil assigns(:ext_system)
#    assert assigns(:ext_system).valid?
#  end
#
#  def test_new
#    get :new
#
#    assert_response :success
#    assert_template 'new'
#
#    assert_not_nil assigns(:ext_system)
#  end
#
#  def test_create
#    num_ext_systems = ExtSystem.count
#
#    post :create, :ext_system => {}
#
#    assert_response :redirect
#    assert_redirected_to :action => 'list'
#
#    assert_equal num_ext_systems + 1, ExtSystem.count
#  end
#
#  def test_edit
#    get :edit, :id => 1
#
#    assert_response :success
#    assert_template 'edit'
#
#    assert_not_nil assigns(:ext_system)
#    assert assigns(:ext_system).valid?
#  end
#
#  def test_update
#    post :update, :id => 1
#    assert_response :redirect
#    assert_redirected_to :action => 'show', :id => 1
#  end
#
#  def test_destroy
#    assert_not_nil ExtSystem.find(1)
#
#    post :destroy, :id => 1
#    assert_response :redirect
#    assert_redirected_to :action => 'list'
#
#    assert_raise(ActiveRecord::RecordNotFound) {
#      ExtSystem.find(1)
#    }
#  end
end
