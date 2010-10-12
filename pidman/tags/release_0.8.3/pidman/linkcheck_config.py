# Set-up all the models you want to use with linklist.
# Import this file in your root url config.

from pidman.pid.models import TargetLinkCheck

RECHECK_AFTER_HOURS = 2
MAX_CHECKS_PER_RUN = 10

RESULTS_PER_PAGE = 25

linklists = {
   'Targets': TargetLinkCheck,
}

