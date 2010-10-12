import psycopg2
from psycopg2 import extras
from mod_python import apache
from mod_python import util
import os
import settings


def handler(req, query):
				   
		# open db connection. this will be used throughout the script
		conn = psycopg2.connect(
                    "dbname=%s user=%s host=%s password=%s" 
                    % (settings.DB_NAME, settings.DB_USER, settings.DB_HOST, settings.DB_PASS)
		)
		
		# split up the URL into meaningful parts
		#req = reqObj.uri[1:] # turns "/foobar" -> "foobar"
		bits = query.split('/', 3) # bits are "/" seperated sections of the URL request string

		# if the type is not "ark:" then resolve it as a purl
		if bits[0] != "ark:":
			pid = bits[0]
			sql, args = "SELECT uri, proxy_id FROM pid_target WHERE noid=%s and qualify=''", [pid]

		# otherwise, it is an ark, so resolve it with qualifier
		else:
			if bits[1] != settings.ARK_NAAN:
                            return notfound(req)
			pid = bits[2]

		# some arks have qualifiers, so we need to include that when querying the db
			if (len(bits) == 4):
					qualify = bits[3]
			else:
					qualify = ''

		# the sql query is set regardless of whether there is a qualifier
			sql, args = "SELECT uri, proxy_id FROM pid_target WHERE noid=%s and qualify=%s", [pid, qualify]

		# now run the query we created above, whether it is a simple purl query or an ark query
		cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) # look for error
		cur.execute(sql, args)
		res = cur.fetchall()
		cur.close()
		   
                # no matches found
                if len(res) == 0:
                    return notfound(req)
                
                # if proxy_id is set, look it up and prepend it to the URL
                row = res[0]
                proxy_id = row[1]
                url = res[0][0]
                
                if type(proxy_id) is int:
                    sql = ("SELECT transform FROM pid_proxy WHERE id=%s" % proxy_id)
                    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                    cur.execute(sql)
                    res = cur.fetchall()
                    cur.close()
                    prefix = res[0][0]
                    url = res[0][0] + url
                    
                # if everything has gone well, we now have a URL, so send a redirect
                util.redirect(req, url)

# display custom 404 error when ark/purl is not found or naan is not recognized
def notfound(req):
    req.status = apache.HTTP_NOT_FOUND
    req.content_type = "text/html"
    pagebuffer = open(os.path.join(settings.ERROR_PAGES_PATH, "404.html"), 'r').read()   
    req.write(pagebuffer)
    return(apache.DONE)

