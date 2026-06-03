import pybgpstream
import datetime
from utils import get_collector_from_ip
from utils_multiproc import parallel_bgp_collection

# Get the collector set from the VP IPs.
collectors_set, asn_set = get_collector_from_ip(vantage_points=param_vp)

print (collectors_set, asn_set)

# The filter to apply.
filter_asn = 'peer {}'.format(' '.join(list(map(lambda x:str(x), list(asn_set)))))

count_dic = parallel_bgp_collection(list(collectors_set), param_time_interval_start, param_time_interval_end, filter_asn, max_workers=max_workers_param, return_count=True)

# Do the ranking.
for peerip, v in sorted(count_dic.items(), key=lambda x:x[1], reverse=True):
    print (peerip, v)
