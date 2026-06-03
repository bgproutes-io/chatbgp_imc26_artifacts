from pyXoXapi import *
import os
import json
from datetime import datetime


answer_file = "../../evaluation/eval_results/OP/answer14.json"

size = 0
time = 0

last_as_set = set()
found = False
bgp2go = set()
selected_vantage_points = get_vantage_points(
    vp_ips=param_vp, 
    ) 

for vantage_point in selected_vantage_points:

    update_data = get_updates(
        [vantage_point],
        return_community = False,
        start_date=param_time_interval_start,
        end_date= param_time_interval_end,  
        prefix_exact_match=[param_prefix], 
        type_filter = 'A',
        details = True,
        ) 

    bgp_updates = update_data.get("data", {}).get("bgp", {})
    time_info = update_data.get("seconds")
    size_info = update_data.get("bytes")
    
    size += size_info or 0
    time += time_info or 0

    for vp_id, update_entries in bgp_updates.items():
        if not update_entries:
            continue
        for update in update_entries:
            as_path = update[3]
            if not as_path:
                continue
            
            bgp2go.add(vantage_point.ip)
            asns = [int(asn) for asn in as_path.split() if asn.isdigit()]
            if len(asns) == 0:
                continue
       
            last_as_set.add(asns[-1])

            if len(last_as_set) > 1:
                
                found = True
                break
         
    if found:
        break

output = {
    "time": time,
    "size": size,
    "final_answer": "Yes" if len(last_as_set) > 1 else "No",
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)