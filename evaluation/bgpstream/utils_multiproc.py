import pybgpstream
from concurrent import futures
import time
from datetime import datetime

def collect_bgp_routes(params_list):
    print ('Start for collector: ', params_list[0])

    # Create a BGPStream instance
    stream = pybgpstream.BGPStream(
        from_time=params_list[1],
        until_time=params_list[2],
        collector=params_list[0],
        record_type='updates',
        filter=params_list[3]
    )
    stream.set_data_interface_option("broker", "cache-dir", "/root/chatbgp/bgpstream/cache")

    upd_list = []
    count_dic = {}

    for rec in stream.records():
        if int(rec.time%10000) == 0:
            print (datetime.fromtimestamp(rec.time))

        for elem in rec:
            if elem.type == 'A':
                if params_list[4]:
                    if elem.peer_address not in count_dic:
                        count_dic[elem.peer_address] = 0
                    count_dic[elem.peer_address] += 1
                else:
                    upd_list.append((elem.time, 
                        elem.peer_address,
                        elem.peer_asn,
                        elem.type,
                        elem.fields['prefix'],
                        elem.fields["as-path"],
                        elem.fields['communities']
                    ))
            elif elem.type == 'W':
                if params_list[4]:
                    if elem.peer_address not in count_dic:
                        count_dic[elem.peer_address] = 0
                    count_dic[elem.peer_address] += 1
                else:
                    upd_list.append((elem.time, 
                        elem.peer_address,
                        elem.peer_asn,
                        elem.type,
                        elem.fields['prefix'],
                        None,
                        None
                    ))


    return upd_list if params_list[4] is False else count_dic

def collect_ribs(params_list):
    print ('Start RIB for collector: ', params_list[0])

    # Create a BGPStream instance
    stream = pybgpstream.BGPStream(
        from_time=params_list[1],
        until_time=params_list[2],
        collector=params_list[0],
        record_type='ribs',
        filter=params_list[3]
    )
    stream.set_data_interface_option("broker", "cache-dir", "/root/chatbgp/bgpstream/cache")

    upd_list = []

    for rec in stream.records():
            for elem in rec:
                if elem.type == 'R':
                    upd_list.append((elem.time, 
                        elem.peer_address,
                        elem.peer_asn,
                        elem.type,
                        elem.fields['prefix'],
                        elem.fields["as-path"],
                        elem.fields['communities']
                    ))

    return upd_list

# Main function to manage parallel processing
def parallel_bgp_collection(collectors, from_time=None, until_time=None, filter=filter, max_workers=4, return_count=False):
    params_query = []
    for c in collectors:
        params_query.append((c, from_time, until_time, filter, return_count)) 

    if not return_count:
        final_result = []
        with futures.ProcessPoolExecutor(max_workers) as executor:
            for result in executor.map(collect_bgp_routes, params_query):
                final_result.extend(result)

        return final_result

    else:
        count_dic_final = {}
        with futures.ProcessPoolExecutor(max_workers) as executor:
            for count_dic in executor.map(collect_bgp_routes, params_query):
                for peerip, v in count_dic.items():
                    count_dic_final[peerip] = v
                    
        return count_dic_final

# Main function to manage parallel processing
def parallel_bgp_ribs(collectors, from_time=None, until_time=None, filter=filter, max_workers=4):
    params_query = []
    for c in collectors:
        params_query.append((c, from_time, until_time, filter)) 

    final_result = []
    with futures.ProcessPoolExecutor(max_workers) as executor:
        for result in executor.map(collect_ribs, params_query):
            final_result.extend(result)

    return final_result

if __name__ == '__main__':
    from_time = "2024-08-01 00:00:00"
    to_time = "2024-08-01 00:00:20"

    collectors = ['RRC26']
    filter=None

    t1 = time.time()
    # records_list = parallel_bgp_collection(collectors, from_time, to_time, filter=filter, max_workers=2)
    records_list = parallel_bgp_ribs(collectors, from_time, to_time, filter=filter, max_workers=2)
    print (len(records_list))
    print (time.time() - t1)