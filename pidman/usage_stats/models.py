from django.conf import settings
from django.db import models
from denorm.fields import MirrorField
from pidman.pid.models import Target
import datetime
from datetime import datetime as dt
from django.db import IntegrityError, transaction

class TargetNotFoundException(Exception):
    pass

class TargetAccessLog(models.Model):
    target = models.ForeignKey(Target)
    ip = models.CharField(max_length=15)
    timestamp = models.DateTimeField()
    referrer = models.CharField(max_length=500, null=True)
    browser = models.CharField(max_length=500)
	
    class Meta:
        unique_together = (('timestamp' , 'ip'), )
        verbose_name = "Access Log"

def get_by_fiscal_year(year):
    try:
        year = int(year)
    except ValueError:
        raise

    start_date = datetime.date(year -1, 10, 1)
    end_date = datetime.date(year, 9, 30)
    return TargetAccessLog.objects.filter(timestamp__range=(start_date, end_date))


def fiscal_years():
    #select distinct month/years from db
    fyears = []
    for datetime in TargetAccessLog.objects.dates('timestamp', 'month'):
        fyears.append(to_fiscal_year(datetime))

    return sorted(list(set(fyears))) #converting to set will remove duplicates

def to_fiscal_year(datetime):
    if datetime.month <= 9:
        return datetime.year
    else:
        return datetime.year + 1


    #noid, qualifier, ip, timestamp, referrer, browser
def createTargetAccessLog(**args):
    try:    
        if not 'qualifier' in args or not args['qualifier']:
            args['qualifier'] = ""

        t = Target.objects.get(noid=args['noid'], qualify=args['qualifier'])

        if 'date_format' in args:
            fmt = args['date_format']
        else:
            fmt = "%d/%b/%Y:%H:%M:%S"

        log = TargetAccessLog(target=t, ip=args['ip'],
            timestamp=dt.strptime(str(args['timestamp'][:-6]), fmt),
            referrer=args['referrer'], browser=args['browser']
        )
        log.save()
        return log
    except IntegrityError:
        # this needs to be caught here so that the tests can run independent of the mgmt cmd parse_access_log.
        print "IntegrityError"
        transaction.rollback()
        return None
    except Target.DoesNotExist, err:
        # this needs to be caught here so that the tests can run independent of the mgmt cmd parse_access_log.
        raise TargetNotFoundException
