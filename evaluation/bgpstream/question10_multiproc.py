import pybgpstream
import datetime
from utils import get_collector_from_ip
from rib_multiproc import get_ribs_multiproc
from utils_multiproc import parallel_bgp_collection

# Get the collector set from the VP IPs.
collectors_set, asn_set = get_collector_from_ip(ip_protocol=param_ip_protocol, vantage_points=param_vp)
print (collectors_set, asn_set)

# The filter to apply.
filter_aspath = 'aspath _{}_ and peer {}'.format(param_asx, ' '.join(list(map(lambda x:str(x), list(asn_set)))))

# Run a binary search from 1 July 2024 until 31 July 2024.
date_low = datetime.datetime.strptime("07-01-2024 00:00:00", "%m-%d-%Y %H:%M:%S")
date_high = datetime.datetime.strptime("08-01-2024 00:00:00", "%m-%d-%Y %H:%M:%S")

changed = None

while (date_high - date_low).total_seconds() >= 86400:
    print (str(param_asx), date_high, date_low)

    # Get the RIB using bgpstream.
    rib_middle = get_ribs_multiproc(datetime.datetime.strftime(date_low + (date_high-date_low)/2, "%m-%d-%Y %H:%M:%S"), collectors_set, filter_aspath, max_workers=max_workers_param)

    # Update the dates.
    if len(rib_middle) > 0:
        date_high = date_low + (date_high-date_low)/2
    else:
        date_low = date_low + (date_high-date_low)/2

updates_list = parallel_bgp_collection(list(collectors_set), datetime.datetime.strftime(date_low, "%m-%d-%Y %H:%M:%S"), datetime.datetime.strftime(date_high, "%m-%d-%Y %H:%M:%S"), filter_aspath, max_workers=max_workers_param)

# Print the first updates where param_asx is in the AS path.
for elem in updates_list:
    print (elem)
    exit(0)

