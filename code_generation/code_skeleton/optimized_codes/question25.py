from pyXoXapi import *
import os
import json
from datetime import datetime


answer_file = "../../evaluation/eval_results/OP/answer25.json"
size = 0
time = 0

detected = False
bgp2go = set()
selected_vantage_points = get_vantage_points(
    vp_ips=param_vp,
    ) 

for vantage_point in selected_vantage_points:
    rib_data = get_rib(
        [vantage_point], 
        date = param_time, 
        return_community = False,
        return_aspath = False,
        prefix_exact_match = [param_prefix],
        return_count = True,
        details = True,
        ) 

    bgp_data = rib_data.get("data", {}).get("bgp", {})
    time_info = rib_data.get("seconds")
    size_info = rib_data.get("bytes")
    
    size += size_info or 0
    time += time_info or 0
    if bgp_data.get(str(vantage_point.unique_id),0) > 0:
        bgp2go.add(vantage_point.ip)
        detected = True
        break
    
output = {
    "time": time,
    "size": size,
    "final_answer": "Yes" if detected else "No",
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)