import pybgpstream
import datetime
from utils import get_collector_from_ip
from rib_multiproc import get_ribs_multiproc

# Get the collector set from the VP IPs.
collectors_set, asn_set = get_collector_from_ip(ip_protocol=param_ip_protocol, vantage_points=param_vp)
print (collectors_set, asn_set)

# The filter to apply.
filter_aspath = 'aspath .*_{}_.* and peer {}'.format(param_asx, ' '.join(list(map(lambda x:str(x), list(asn_set)))))

rib = get_ribs_multiproc(param_time, list(collectors_set), filter_aspath, max_workers=max_workers_param)
print (rib)

neighbors = set()
for peerip in rib:
    # We need this because we can only match on VP's asn and not peer address.
    if peerip in param_vp:
        for prefix in rib[peerip]:
            aspath = rib[peerip][prefix]
            if int(param_asx) in aspath and len(aspath) > 1:
                for i in range(0, len(aspath)-1):
                    if aspath[i] == param_asx and aspath[i+1] != param_asx:
                        neighbors.add(aspath[i+1])
                    
                # If param_asx is the last AS.
                if aspath[-1] == param_asx and aspath[-2] != param_asx:
                    neighbors.add(aspath[-2])

print (neighbors)
# print (','.join(list(map(lambda x:str(x), list(neighbors)))))
