REST API
--------

.. automodule:: pidman.rest_api
   :members:

.. rest_api module docs provides an overview of the api and available
   endpoints

Example use
^^^^^^^^^^^

When using the PID manager API from Python, we recommend
`pidmanclient <https://github.com/emory-libraries/pidmanclient>`_.

Ruby
****

Ruby code to create a new ARK (example from
`GeoServer-Workflow <https://github.com/emory-libraries-ecds/GeoServer-Workflow>`_).

.. code-block:: ruby

  def create_ark()
    # Private method to create an ARK via the pidman REST API.
    pidman_auth = {
      username: $config['pidman_user'],
      password: $config['pidman_pass']
    }

    response = HTTParty.post \
      'https://testpid.library.emory.edu/ark/', \
      body: "domain=#{$config['pidman_domain']}&target_uri=myuri.org&name=#{self.metadata['title']}", \
      basic_auth: pidman_auth
    # The response will give us the full URL, we just want the PID.
    if  "#{response.code}" == '201'
      return response.body.split('/')[-1]
    else
      $logger.error "Failed to create ARK for #{self.file_name}. Response was #{response.code}"
    end
  end


Curl
****

List domains:

.. code-block:: shell

    curl https://testpid.library.emory.edu/domains/

Create a new domain using POST:

.. code-block:: shell

    curl -X POST --user curler:curlerpass --data "name=my+domain" \
        https://testpid.library.emory.edu/domains/
    curl -X POST --user curler:curlerpass \
        --data "name=seb+domain&parent=http://testpid.library.emory.edu/domains/1/" \
        https://testpid.library.emory.edu/domains/

Update a domain with PUT and JSON data:

.. code-block:: shell

    curl -X PUT --user curler:curlerpass -H "Content-Type: application/json" \
        --data '{"name": "my subdomain"}' \
        http://testpid.library.emory.edu/domains/3/

Create a new PURL or ARK:

.. code-block:: shell

    curl -X POST --user curler:curlerpass --data \
        "domain=http://localhost:8000/domains/1/&target_uri=http://example.com&name=my+pid" \
        http://localhost:8000/purl/

    curl -X POST --user curler:curlerpass --data \
        "domain=http://localhost:8000/domains/1/&target_uri=http://example.com/foo&name=my+ark&qualifier=foo" \
        http://localhost:8000/ark/

View and update an ARK:

.. code-block:: shell

    curl http://pids.co/ark/22
    curl -X PUT --user curler:curlerpass -H "Content-Type: application/json" \
        --data '{"name": "an updated ARK"}' \
        http://pids.co/ark/22

Create or update and delete ARK targets:

.. code-block:: shell

    curl -X PUT --user curler:curlerpass -H "Content-Type: application/json" \
        --data '{"target_uri": "http://example.com/new/", "active": true}' \
        http://localhost:8000/ark/22/qualifier
    curl -X DELETE --user curler:curlerpass http://pids.co/ark/22/qualifier


----------


.. automodule:: pidman.rest_api.views
   :members:

.. automodule:: pidman.rest_api.decorators
   :members:
