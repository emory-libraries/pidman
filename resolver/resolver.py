#!/usr/bin/python
 
import os, cgi, sys, pyPgSQL, CGIHTTPServer, SocketServer
from pyPgSQL import PgSQL

from config import config

# get global configuration
conf=config()

conn = PgSQL.connect(
    "%s:%s:%s:%s:%s" 
    % (conf.DB_HOST, conf.DB_PORT, conf.DB_NAME, conf.DB_USER, conf.DB_PASS)
    )

# our resolver is just overriding the do_GET method of CGIHTTPServer.
class Handler(CGIHTTPServer.CGIHTTPRequestHandler):  

    server_version = conf.VERSION
    
    def do_GET(self):
        
        # the "documentroot" is a configurable redirect
        if self.path == '/':
            self.send_response(303)
            self.send_header("Location", conf.MANAGE_URL)
            self.end_headers()

        # if they're not asking for the management url, assume the request is 
        # to resolve a pid. do it:
        else: 
        
            # send 500 if we can't get a response from the database
           
            try:
		# split up the URL into meaningful parts
                req = self.path[1:] # turns "/foobar" -> "foobar"
		bits = req.split('/', 3)

		# if the type is not "ark:" then resolve it as a purl
		if bits[0] != "ark:":
			pid = bits[0]
			sql = ("SELECT uri, proxy_id FROM targets WHERE pid='%s' and qualify is null" % pid)
		# otherwise, it is an ark, so resolve it with qualifier
		else:
			if (bits[1] != conf.NAAN):
				self.send_error(404)
				return

			pid = bits[2]

			if (len(bits) == 4):
				qualifier = ("= '%s'" % bits[3])
			else:
				qualifier = ("is null")

			sql = ("SELECT uri, proxy_id FROM targets WHERE pid='%s' and qualify %s" % (pid, qualifier))

                cur = conn.cursor() # look for error
                cur.execute(sql)
                res = cur.fetchall()
                cur.close()
            except:
                self.send_error(500) #internal server error
                return
           
            # if proxy_id is set, look it up and prepend it to the URL
	    proxy_id = res[0][1]
	    url = res[0][0]
	    if type(proxy_id) is int:
	        sql = ("SELECT transform FROM proxies WHERE id=%s" % proxy_id)
		cur = conn.cursor()
		cur.execute(sql)
		res = cur.fetchall()
		cur.close()
		
		prefix = res[0][0]
	    	url = res[0][0] + url
	    
            # send 303 (temporarily moved) if we found it or 404 if we didn't
            try: 
                self.send_response(303) #temporarily moved
                self.send_header("Location", url)
                self.end_headers()
            except:
                self.send_error(404) #not found

# run server
httpd = SocketServer.ThreadingTCPServer((conf.INTERFACE, conf.RESOLVER_PORT), Handler)
print Handler.server_version + " resolver listening on " + conf.INTERFACE + ":" + str(conf.RESOLVER_PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print "Terminated by keyboard interrupt"
    sys.exit(0)

