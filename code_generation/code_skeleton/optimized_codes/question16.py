from pyXoXapi import *
import os
import json
from datetime import datetime


answer_file = "../../evaluation/eval_results/OP/answer16.json"
size = 0
time = 0

vp_and_nb_updates_tuple = []
bgp2go  =set()
selected_vantage_points = get_vantage_points(
    vp_ips=param_vp, 
    ) 

for vantage_point in selected_vantage_points:
   
    update_data = get_updates(
        [vantage_point],
        return_community = False,
        return_aspath = False,
        start_date=param_time_interval_start,
        end_date= param_time_interval_end,  
        return_count = True,
        details = True,
        ) 

    bgp_updates = update_data.get("data", {}).get("bgp", {})
    time_info = update_data.get("seconds")
    size_info = update_data.get("bytes")
    
    size += size_info or 0
    time += time_info or 0
    vp_updates = bgp_updates.get(str(vantage_point.unique_id))

    if vp_updates is None:
        continue
    
    bgp2go.add(vantage_point.ip)
    
    number_of_withdrawals = bgp_updates.get(str(vantage_point.unique_id)).get("W",0)
    number_of_announcements = bgp_updates.get(str(vantage_point.unique_id)).get("A",0)
    
    number_of_updates = number_of_announcements + number_of_withdrawals

    vp_and_nb_updates_tuple.append({
        'vp': str(vantage_point.unique_id), 
        'updates':number_of_updates})

output = {
    "time": time,
    "size": size,
    "final_answer": sorted(vp_and_nb_updates_tuple, key=lambda x: x['updates'], reverse=True),
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)