import pybgpstream
import datetime
from utils import get_collector_from_ip
from utils_multiproc import parallel_bgp_collection

# Get the collector set from the VP IPs.
collectors_set, asn_set  = get_collector_from_ip(vantage_points=param_vp)
print (collectors_set, asn_set)

# The filter to apply.
filter_prefix = 'prefix exact {} and peer {}'.format(param_prefix, ' '.join(list(map(lambda x:str(x), list(asn_set)))))
print (filter_prefix)


updates_list = parallel_bgp_collection(list(collectors_set), param_time_interval_start, param_time_interval_end, filter_prefix, max_workers=max_workers_param)

last_as_set = set()

# Iterate over the updates
for elem in updates_list:
    if elem[1] in param_vp:
        if elem[3] == 'A':
            last_as_set.add(elem[5].split(" ")[-1])
            if len(last_as_set) > 1:
                print (last_as_set)
                exit(0)
                
print (last_as_set)
