import pybgpstream
from datetime import timedelta
import datetime
from utils import get_collector_from_ip
from utils_multiproc import parallel_bgp_collection

cur_paramvp = param_vp
date_cur = datetime.datetime.strptime("08-01-2024 00:00:00", "%m-%d-%Y %H:%M:%S")

res_dic = {}
vp_done = set()

while len(cur_paramvp) > 0 and date_cur >= datetime.datetime.strptime("07-01-2024 00:00:00", "%m-%d-%Y %H:%M:%S"):
    print (date_cur)
    print (res_dic)

    # Get the collector set from the VP IPs.
    # WARNING: Ensure that param_vp includes all the VPs when the script is called!!!
    collectors_set, asn_set = get_collector_from_ip(vantage_points=cur_paramvp)
    print (collectors_set, asn_set)

    # The filter to apply.
    filter_prefix = 'prefix exact {} and peer {}'.format(param_prefix, ' '.join(list(map(lambda x:str(x), list(asn_set)))))

    updates_list = parallel_bgp_collection(list(collectors_set), datetime.datetime.strftime(date_cur - timedelta(minutes=60), "%m-%d-%Y %H:%M:%S"), datetime.datetime.strftime(date_cur, "%m-%d-%Y %H:%M:%S"), filter_prefix, max_workers=max_workers_param)

    # Store the timestamp of the last update seen for every VP for the given prefix.
    for elem in updates_list:
        print (elem)
        if elem[1] not in res_dic:
            res_dic[elem[1]] = elem[0]
            vp_done.add(elem[1])

    for vp in vp_done:
        if vp in cur_paramvp:
            cur_paramvp.remove(vp)

    date_cur = date_cur - timedelta(minutes=60)

for vp in res_dic:
    print (vp, res_dic[vp])