from pyXoXapi import *
from collections import defaultdict
import os
import json
from datetime import datetime


answer_file = "../../evaluation/eval_results/OP/answer31.json"
size = 0
time = 0
rib_sizes = defaultdict(int)
bgp2go = set()
selected_vantage_points = get_vantage_points(
    vp_ips=param_vp, 
    ) 

for vantage_point in selected_vantage_points:
    number_of_entries = get_rib(
        [vantage_point], 
        date = param_time, 
        return_community = False,
        return_aspath = False,
        return_count = True,
        details = True,
        ) 

    bgp_data = number_of_entries.get("data", {}).get("bgp", {})
    time_info = number_of_entries.get("seconds")
    size_info = number_of_entries.get("bytes")
    
    size += size_info or 0
    time += time_info or 0
    
    r_size = bgp_data.get(str(vantage_point.unique_id),0)
    
    bgp2go.add(vantage_point.ip)
    
    rib_sizes[str(vantage_point.unique_id)] = r_size

output = {
    "time": time,
    "size": size,
    "final_answer": rib_sizes,
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)