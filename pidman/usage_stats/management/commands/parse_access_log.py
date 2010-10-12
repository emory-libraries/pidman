from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import sys
import re
from django.conf import settings
from pidman.usage_stats.models import createTargetAccessLog, TargetNotFoundException

class Command(BaseCommand):
	
    # this should be setup as a cron to input files from /var/share/httpd/purl_access_log
    #  ./manage.py parse_access_log -f /var/share/https/purl_access_log -o /var/share/https/parse_accss_log.err
    option_list = BaseCommand.option_list + (
        make_option('-f', help='Input Apache Access Log.', default='/var/log/httpd/purl_access_log', dest='input_log'),
        make_option('-o', help='Invalid Target Log.', default=None, dest='notfound_log'),
     )
	# /var/log/https/purl_access_log
    help = 'Parse Access Log'
    args = '[appname ...]'	

    # this is standard log format
    parts = [
        r'(?P<ip>\S+)',                     # ip %h
        r'\S+',                             # indent %l (unused)
        r'(?P<user>\S+)',                   # user %u
        r'\[(?P<timestamp>.+)\]',           # time %t
        r'"(?P<request>.+)"',               # request "%r"
        r'(?P<status>[0-9]+)',              # status %>s
        r'(?P<size>\S+)',                   # size %b (careful, can be '-')
        r'"(?P<referrer>.*)"',              # referrer "%{Referrer}i"
        r'"(?P<browser>.*)"',               # user agent "%{User-agent}i"
    ]

    #global regular expression patterns
    pattern = re.compile(r'\s+'.join(parts)+r'\s*\Z')

    #exclusion patterns
    request_pattern = re.compile('|'.join(settings.USAGE_LOG_EXCLUDE_REQUEST_PATTERNS))
    browser_pattern = re.compile('|'.join(settings.USAGE_LOG_EXCLUDE_AGENTS_PATTERNS))

    noid_pattern_str = '^GET (/ark:/%(NAAN)s)?/([0-9A-z]*)/?([0-9A-z]*)/?.*' % {'NAAN': settings.PID_ARK_NAAN}
    noid_pattern = re.compile(noid_pattern_str)

    def handle(self, *fixture_labels, **options):
        inputfile    = options.get('input_log', None)
        notfound_log = options.get('notfound_log', None)

        fi = None
        ti = None
        try:
            #open file
            fi = open(inputfile, 'r')
            if notfound_log:
                ti = open(notfound_log, 'a')
            #read the log file line by line.
            for line in fi:
                # parse the line into the named parameters
                res = self.parse(line)
                if res:
                    try:
                        # createTargetAccessLog is found in usage_stats/models.py
                        # grab noid and qualifier from res dict group
                        # look the target up via Pid and Target tables,
                        # if target found write info to new table usage_stats_targetaccesslog.
                        createTargetAccessLog(**res)
                    except TargetNotFoundException:
                        if notfound_log:
                            ti.write(line)
        except IOError, err:
            print err
        finally:
            if fi:
                fi.close()
            if notfound_log and ti:
                ti.close()

    def parse(self, line):
        #parse data into dict
        m = self.pattern.match(line)
        if not m:
            return None

        res = m.groupdict()

        #exclude resolver redirects and other request matches
        if self.request_pattern.search(res['request']):
            return None

        #exclude based on user agent
        if self.browser_pattern.match(res['browser']):
            return None

        #exclude by ip
        if res["ip"] in settings.USAGE_LOG_EXCLUDE_IPS:
            return None

        # Log indicates null values as dash.
        if res["user"] == "-":
            res["user"] = None

        res["status"] = int(res["status"])

        if res["size"] == "-":
            res["size"] = 0
        else:
            res["size"] = int(res["size"])

        if res["referrer"] == "-":
            res["referrer"] = None


        m = self.noid_pattern.search(res['request'])
        if m:
            res['noid'] = m.group(2)
            if m.group(3):
                res['qualifier'] = m.group(3)
            else:
                res['qualifier'] = None

            return res
        else:
            return None
