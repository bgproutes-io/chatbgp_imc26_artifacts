import pybgpstream
import datetime
from utils import get_collector_from_ip
from rib_multiproc import get_ribs_multiproc

# Get the collector set from the VP IPs.
collectors_set, asn_set = get_collector_from_ip(ip_protocol=param_ip_protocol, vantage_points=param_vp)
print (collectors_set, asn_set)

# Filter to apply.
filter_peer = 'peer {}'.format(' '.join(list(map(lambda x:str(x), list(asn_set)))))

# Get the RIB using bgpstream.
rib = get_ribs_multiproc(param_time, collectors_set, filter_peer, max_workers=max_workers_param)

nb_single_hop_aspaths = 0
nb_all_paths = 0
for peerip in rib:
    # We need this because we can only match on VP's asn and not peer address.
    if peerip in param_vp: 
        for prefix in rib[peerip]:
            aspath = rib[peerip][prefix]
            nb_all_paths += 1
            if len(aspath) == 2:
                nb_single_hop_aspaths += 1

print ('percentage of single hop AS path: {}'.format(float(nb_all_paths)/float(nb_single_hop_aspaths)))