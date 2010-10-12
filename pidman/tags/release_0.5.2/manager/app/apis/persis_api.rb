class PersisApi < ActionWebService::API::Base
  api_method :generateArk,
             :expects => [{:username => :string}, 
                          {:password => :string}, 
                          {:uri => :string}, 
                          {:name => :string},
                          {:qualifier => :string},
                          {:domain_id => :int},
                          {:proxy_id => :int},
                          {:external_system => :string},
                          {:external_system_key => :string}],
             :returns => [{:ark => :string}]
  
  api_method :generatePurl,
             :expects => [{:username => :string}, 
                          {:password => :string}, 
                          {:uri => :string}, 
                          {:name => :string},
                          {:domain_id => :int},
                          {:proxy_id => :int},                         
                          {:external_system => :string},
                          {:external_system_key => :string}],                          
             :returns => [{:purl => :string}] 
  
  api_method :addArkTarget,
             :expects => [{:username => :string},
                          {:password => :string},
                          {:noid => :string},
                          {:qualifier => :string},
                          {:uri => :string},
                          {:proxy_id => :int}],
             :returns => [{:ark => :string}]
             
  api_method :editTarget,
             :expects => [{:username => :string},
                          {:password => :string},
                          {:purl => :string},
                          {:uri => :string}],
             :returns => [{:purl => :string}]
                         
#  api_method :listDomains => [{:username => :string}],
#             :returns => [Domain]    
end
