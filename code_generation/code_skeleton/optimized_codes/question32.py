from pyXoXapi import *
import os
import json
from datetime import datetime


answer_file = "../../evaluation/eval_results/OP/answer32.json"
size = 0
time = 0

distinct_communities = set()
bgp2go = set()
selected_vantage_points = get_vantage_points(
    vp_ips=param_vp, 
    ) 

for vantage_point in selected_vantage_points:
    rib_data = get_rib(
        [vantage_point], 
        date = param_time, 
        return_aspath = False,
        return_community = True,
        community_regexp='( |^)'+str(param_asx)+':.*',
        details = True,
        ) 

    bgp_data = rib_data.get("data", {}).get("bgp", {})
    time_info = rib_data.get("seconds")
    size_info = rib_data.get("bytes")
    
    size += size_info or 0
    time += time_info or 0
    
    for vp_id, prefix_data in bgp_data.items():
        
        for prefix, entry in prefix_data.items():
           
            community_list = entry[1]
            if not community_list:
                continue
            
            bgp2go.add(vantage_point.ip)
    
            for community in community_list.split(' '):
        
                if community.startswith(str(param_asx)+':'):
                    distinct_communities.add(community)

output = {
    "time": time,
    "size": size,
    "final_answer": len(distinct_communities),
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)
            