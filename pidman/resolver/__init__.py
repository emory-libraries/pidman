'''Public-facing resolver that redirects ARK and PURLs URLs to their
Target URLs.  Provides minimal metadata and policy information
for an ARK when one or two question marks follow the ARK URL.

(Metadata responses are based on the ARK spec 5.1.2 generic
description service and 5.1.1 generic policy service.)

URLs are configured in Django localsettings using
**PID_RESOLVER_URL** and **PID_ARK_NAAN**.
'''
