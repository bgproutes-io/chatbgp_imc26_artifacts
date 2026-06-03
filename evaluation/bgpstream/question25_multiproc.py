import pybgpstream
import datetime
from utils import get_collector_from_ip
from rib_multiproc import get_ribs_multiproc

# Get the collector set from the VP IPs.
collectors_set, asn_set = get_collector_from_ip(vantage_points=param_vp)
print (collectors_set, asn_set)

# The filter to apply.
filter_prefix = 'prefix exact {} and peer {}'.format(param_prefix, ' '.join(list(map(lambda x:str(x), list(asn_set)))))
print (filter_prefix)

rib = get_ribs_multiproc(param_time, collectors_set, filter_prefix, max_workers=max_workers_param)

for peerip in rib:
    if peerip in param_vp:
        if param_prefix in rib[peerip]:
            print ('Yes')
            exit(0)

print ('No')

