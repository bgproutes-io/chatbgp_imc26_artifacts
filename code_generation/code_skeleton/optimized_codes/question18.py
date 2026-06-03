from pyXoXapi import *
import os
import json
from datetime import datetime


answer_file = "../../evaluation/eval_results/OP/answer18.json"
size = 0
time = 0

# RFC7999 BLACKHOLE community value is 65535:666.
blackholing_community_regexp = r'(^| )65535:666( |$)'

bgp2go = set()
desired_updates = []
selected_vantage_points = get_vantage_points(
    vp_ips=param_vp, 
    ) 

for vantage_point in selected_vantage_points:

    update_data = get_updates(
        [vantage_point],
        return_community = True,
        start_date=param_time_interval_start,
        end_date= param_time_interval_end,  
        community_regexp = '(^| )'+blackholing_community_regexp+'( |$)',
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
        bgp2go.add(vantage_point.ip)
        for update in update_entries:
            desired_updates.append(update)
        
output = {
    "time": time,
    "size": size,
    "final_answer": desired_updates,
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)

