require File.dirname(__FILE__) + '/../test_helper'
require 'persis_controller'

class PersisController; def rescue_action(e) raise e end; end

class PersisControllerApiTest < Test::Unit::TestCase
  def setup
    @controller = PersisController.new
    @request    = ActionController::TestRequest.new
    @response   = ActionController::TestResponse.new
  end

  def test_truth
    assert true
  end

#  def test_generateArk
#    result = invoke :generateArk
#    assert_equal nil, result
#  end
#
#  def test_generatePurl
#    result = invoke :generatePurl
#    assert_equal nil, result
#  end
end
