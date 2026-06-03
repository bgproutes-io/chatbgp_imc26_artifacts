from pyXoXapi import *
import os
import json
from datetime import datetime


answer_file = "../../evaluation/eval_results/OP/answer30.json"
size = 0
time = 0

prefixes_24 = set()

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
        aspath_regexp='(^| )'+str(param_asx)+'$',
        details = True,
        ) 

    bgp_data = rib_data.get("data", {}).get("bgp", {})
    time_info = rib_data.get("seconds")
    size_info = rib_data.get("bytes")
    
    size += size_info or 0
    time += time_info or 0
    
    for vp_id, prefix_data in bgp_data.items():
        if not prefix_data:
            continue
        bgp2go.add(vantage_point.ip)
        for prefix in prefix_data.keys():
            if prefix.endswith("/24"):
                prefixes_24.add(prefix)

output = {
    "time": time,
    "size": size,
    "final_answer": len(prefixes_24),
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)

                          
