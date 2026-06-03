from pyXoXapi import *
import os
import json
from datetime import datetime


answer_file = "../../evaluation/eval_results/OP/answer9.json"

size = 0
time = 0

ases_int_the_middle = set()
ases_at_the_ends = set()
bgp2go = set()
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
            if len(asns) == 0:
                continue
            
            for asn in asns[1:-1]:
                ases_int_the_middle.add(asn)
                
            ases_at_the_ends.add(asns[0])
            ases_at_the_ends.add(asns[-1])
                          
output = {
    "time": time,
    "size": size,
    "final_answer": len(ases_int_the_middle.difference(ases_at_the_ends)),
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)