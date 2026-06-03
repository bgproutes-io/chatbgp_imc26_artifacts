from pyXoXapi import *
import os
import json
from datetime import datetime


answer_file = "../../evaluation/eval_results/OP/answer39.json"
size = 0
time = 0

community_set = set()
bgp2go = set()
selected_vantage_points = get_vantage_points(
    vp_ips=param_vp, 
    ) 

for vantage_point in selected_vantage_points:
    rib_data = get_rib(
        [vantage_point], 
        date = param_time, 
        return_community = True,
        return_aspath = False,
        prefix_exact_match = [param_prefix],
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
        for prefix, entry in prefix_data.items():
         
            # Second field = Community String
            community_str = entry[1]
            if not community_str:
                continue
        
            community_list = community_str.split()
            
            for community_value in community_list:
                community_set.add(community_value)
 
output = {
    "time": time,
    "size": size,
    "final_answer": list(community_set),
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)

