require File.dirname(__FILE__) + '/../test_helper'
require 'persis_controller'

class PersisController; def rescue_action(e) raise e end; end

class PersisApiTest < Test::Unit::TestCase

  fixtures :pids, :targets, :domains, :users

  def setup
    @controller = PersisApiController.new
    @request    = ActionController::TestRequest.new
    @response   = ActionController::TestResponse.new
  end

  def test_generateArk
  	u = users(:second)
  
    result = invoke :generateArk, 'test_user', 'test', 'New York Times Online', 'http://www.nytimes.com', 'qualifier', 1, nil, nil, nil
    assert_match Regexp.new("^#{ID_SERVER_URL}/ark:/#{EMORY_ARK_NAAN}/[A-Za-z0-9]{2,}/qualifier$"), result
  end
    
 
  def test_generatePurl
    result = invoke :generatePurl, 'test_user', 'test', 'New York Times Online', 'http://www.nytimes.com', 1, nil, nil, nil
    assert_match Regexp.new("^#{ID_SERVER_URL}/[A-Za-z0-9]{2,}$"), result
  end
end
