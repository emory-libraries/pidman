from linkcheck import Linklist
from pidman.pid.models import Target

class TargetLinklist(Linklist):
    model = Target
    url_fields = ['uri']
    object_filter = {'active': True}


linklists = {'Targets': TargetLinklist}
