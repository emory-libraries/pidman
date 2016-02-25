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
      'https://pidserver.io/ark/', \
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

    curl https://pidserver.io/domains/

Create a new domain using POST:

.. code-block:: shell

    curl -X POST --user user:pass --data "name=my+domain" \
        https://pidserver.io/domains/
    curl -X POST --user user:pass \
        --data "name=seb+domain&parent=http://pidserver.io/domains/1/" \
        https://pidserver.io/domains/

Update a domain with PUT and JSON data:

.. code-block:: shell

    curl -X PUT --user user:pass -H "Content-Type: application/json" \
        --data '{"name": "my subdomain"}' \
        http://pidserver.io/domains/3/

Create a new PURL or ARK:

.. code-block:: shell

    curl -X POST --user user:pass --data \
        "domain=http://pidserver.io/domains/1/&target_uri=http://example.com&name=my+pid" \
        http://pidserver.io/purl/

    curl -X POST --user user:pass --data \
        "domain=http://pidserver.io/domains/1/&target_uri=http://example.com/foo&name=my+ark&qualifier=foo" \
        http://pidserver.io/ark/

View and update an ARK:

.. code-block:: shell

    curl http://pidserver.io/ark/22
    curl -X PUT --user user:pass -H "Content-Type: application/json" \
        --data '{"name": "an updated ARK"}' \
        http://pidserver.io/ark/22

Create or update and delete ARK targets:

.. code-block:: shell

    curl -X PUT --user user:pass -H "Content-Type: application/json" \
        --data '{"target_uri": "http://example.com/new/", "active": true}' \
        http://pidserver.io/ark/22/qualifier
    curl -X DELETE --user user:pass http://pidserver.io/ark/22/qualifier


PHP
***

.. code-block:: PHP

    <?php
     // get information about all domains
     $data = json_decode(file_get_contents('http://pidserver.io/domains/'));
     // get a single domain
     $data = json_decode(file_get_contents('http://pidserver.io/domains/1/'));
     print "Domain " . $data->{'name'} . " with uri " . $data->{'uri'} .
        " has " . $data->{"number of pids"} . " pids\n";

    // generate a new ark
    $username = 'user';
    $password = 'password';
    $payload = array('domain' => 'http://pidserver.io/domains/1/',
    'name'=> 'php ark', 'target_uri' => 'http://fr.php.net/file_get_contents');
    $ch = curl_init('http://pidserver.io/ark/');
    curl_setopt($ch, CURLOPT_USERPWD, $username . ":" . $password);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    curl_setopt($ch, CURLOPT_POST, TRUE);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
    $ark = curl_exec($ch);
    curl_close($ch);
    ?>

----------


.. automodule:: pidman.rest_api.views
   :members:

.. automodule:: pidman.rest_api.decorators
   :members:
