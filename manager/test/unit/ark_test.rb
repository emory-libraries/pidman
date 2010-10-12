require File.dirname(__FILE__) + '/../test_helper'

class ArkTest < Test::Unit::TestCase
  fixtures :pids, :targets, :domains, :users

  # Replace this with your real tests.
  def test_truth
    assert true
  end
  
  def test_targets_assoc
    p = pids(:ark)
    
    assert p.is_a?(Ark)
    
    assert_equal "http://www.cnn.com", p.targets[0].uri
  end
  
  def test_create_ark
    u = users(:first)
    
    a = Ark.find_by_name("Google Maps")
    assert_nil a
  
    a = Ark.generate(
      :user       => u, 
      :domain_id  => 1,
      :name       => 'Google Maps',
      :uri        => 'http://maps.google.com', 
      :qualifier  => '?',
      :proxy_id   => nil
    )
    
    a = Ark.find_by_name("Google Maps")
    assert a #test that p is not nil
    
    assert_equal 1, a.creator_id
    assert_equal 1, a.modified_by
    assert_equal 1, a.domain_id
    
    assert a.targets
    assert_equal a.pid, a.targets[0].pid
    assert_equal 'http://maps.google.com', a.targets[0].uri
    assert_equal '?', a.targets[0].qualify
    
  end  
  
  def test_update_ark
    u = users(:first)
    
    a = Ark.find_by_pid("2dc1")
    assert a
    assert_equal('CNN Online', a.name)
  
    n = Ark.find(:all).size
    
    b = Ark.update(u, '2dc1', 'FoxNews', 'http://www.foxnews.com', '?')    
    assert b #test that a is not nil
    assert_equal n, Ark.find(:all).size
    
    assert_equal(a.pid, b.pid)
    assert_equal(a.id, b.id)
    assert_not_equal(a.name, b.name)
    assert_equal('FoxNews', b.name)
    
    assert_equal 1, a.creator_id
    assert_equal 1, a.modified_by
    assert_equal 1, a.domain_id
    assert_not_equal a.updated_at, a.created_at
    
    assert a.targets
    assert_equal a.pid, a.targets[1].pid
    assert_equal 'http://www.foxnews.com', a.targets[1].uri
    assert_equal '?', a.targets[1].qualify
    
  end    

end
