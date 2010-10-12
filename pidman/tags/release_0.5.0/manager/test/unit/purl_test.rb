require File.dirname(__FILE__) + '/../test_helper'

class PurlTest < Test::Unit::TestCase
  fixtures :pids, :targets, :domains, :users

  # Replace this with your real tests.
  def test_truth
    assert true
  end
  
  def test_targets_assoc
    p = pids(:purl)
    assert_equal "http://www.emory.edu", p.targets[0].uri
  end
  
  def test_create_purl
    u = users(:first)
    
    p = Purl.find_by_name("The Onion")
    assert_nil p
  
    p = Purl.generate(
      :user       => u, 
      :domain_id  => 1,
      :name       => 'The Onion', 
      :uri        => 'http://www.onion.com',
      :proxy_id   => 0,
      :ext_system_id  => nil,
      :ext_system_key => ''
    )    
    assert p #test that p is not nil
    
    assert_equal 1, p.creator_id
    assert_equal 1, p.modified_by
    assert_equal 1, p.domain_id
    
    assert_equal 1, p.targets.size
    assert_equal p.pid, p.targets[0].pid
    assert_equal 'http://www.onion.com', p.targets[0].uri
    assert_nil p.targets[0].qualify
    
  end
end
