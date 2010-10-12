require File.dirname(__FILE__) + '/../test_helper'

class TargetTest < Test::Unit::TestCase
  fixtures :pids, :targets, :domains, :users
  
  # Replace this with your real tests.
  def test_truth
    assert true
  end
  
  def test_targets_assoc
    t = targets(:ark)
    assert_instance_of Ark, t.Pid
    
    t = targets(:purl)
    assert_instance_of Purl, t.Pid
  end
  
  def test_purl_url
    t = targets(:purl)
    assert_equal ID_SERVER_URL + '/2dbx', t.getURL
  end
  
  def test_ark_url
    t = targets(:ark)
    
    assert_equal ID_SERVER_URL + "/ark:/" + EMORY_ARK_NAAN + "/2dc1/?", t.getURL
  end
end