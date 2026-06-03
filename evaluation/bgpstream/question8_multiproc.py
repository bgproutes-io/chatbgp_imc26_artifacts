import pybgpstream
import datetime
from utils import get_collector_from_ip
from rib import get_ribs
from rib_multiproc import get_ribs_multiproc

# Get the collector set from the VP IPs.
collectors_set, asn_set = get_collector_from_ip(ip_protocol=param_ip_protocol, vantage_points=param_vp)
print (collectors_set, asn_set)

# Filter to apply.
filter_peer = 'peer {}'.format(' '.join(list(map(lambda x:str(x), list(asn_set)))))

# Get the RIB using bgpstream.
rib = get_ribs_multiproc(param_time, collectors_set, filter_peer, max_workers=max_workers_param)

# Set that will contain all the ASes that appear in the middle of an AS path.
ASes_in_the_middle = set()

# Set with all ASes.
all_ases = set()

for peerip in rib:
    # We need this because we can only match on VP's asn and not peer address.
    if peerip in param_vp: 
        for prefix in rib[peerip]:
            aspath = rib[peerip][prefix]

            for asn in aspath:
                all_ases.add(asn)

            for asn in aspath[1:-1]:
                ASes_in_the_middle.add(asn)

# Print all ASes that are not in the middle.
print (len(all_ases.difference(ASes_in_the_middle)))
