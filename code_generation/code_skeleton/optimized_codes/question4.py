from pyXoXapi import *
import os
import json
from datetime import datetime


answer_file = "../../evaluation/eval_results/OP/answer4.json"

size = 0
time = 0

middle_ases = set()
bgp2go = set()
AS_stub_dic = {}

selected_vantage_points = get_vantage_points(
    vp_ips=param_vp, 
    data_afi = param_ip_protocol,
    ) 

for vantage_point in selected_vantage_points:

    rib_data = get_rib(
        [vantage_point], 
        date = param_time, 
        return_community = False,
        details = True,
        ) 

    bgp_data = rib_data.get("data", {}).get("bgp", {})
    time_info = rib_data.get("seconds")
    size_info = rib_data.get("bytes")
    
    size += size_info or 0
    time += time_info or 0
    

    for vp_id, prefix_data in bgp_data.items():
        
        for prefix, entry in prefix_data.items():
           
            as_path = entry[0]
            if not as_path:
                continue
            
            bgp2go.add(vantage_point.ip)
            
            asns = [int(asn) for asn in as_path.split() if asn.isdigit()]
            
            if len(asns) < 2:
                continue

            if asns[0] not in AS_stub_dic:
                AS_stub_dic[asns[0]] = set()
            AS_stub_dic[asns[0]].add(asns[1])
        
            if asns[-1] not in AS_stub_dic:
                AS_stub_dic[asns[-1]] = set()
            AS_stub_dic[asns[-1]].add(asns[-2])
                
            for asn in asns[1:-1]:
                middle_ases.add(asn)
                     
returned_ases = set()

for asn in AS_stub_dic:
    if asn not in middle_ases:
        if len(AS_stub_dic[asn]) > 1:
            returned_ases.add(asn)

output = {
    "time": time,
    "size": size,
    "final_answer": sorted(list(returned_ases)),
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)
