from pyXoXapi import *
from datetime import datetime, timedelta
import numpy as np
import os
import json


answer_file = "../../evaluation/eval_results/OP/answer15.json"
size = 0
time = 0

bgp2go = set()
nb_updates_targeted_time_period = 0
nb_updates_other_time_periods = []


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
        type_filter = 'W',
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
    nb_updates_targeted_time_period += number_of_withdrawals

for period_shift_day in range (1, 10):
    start_date_tmp = datetime.strptime(param_time_interval_start, '%Y-%m-%dT%H:%M:%S') - timedelta(days=period_shift_day)
    end_date_tmp = datetime.strptime(param_time_interval_end, '%Y-%m-%dT%H:%M:%S') - timedelta(days=period_shift_day)
    
    nb_updates_other_time_periods.append(0)
        
    for vantage_point in selected_vantage_points:
        update_data = get_updates(
            [vantage_point], 
            return_aspath = False,
            return_community = False, 
            start_date=start_date_tmp.strftime('%Y-%m-%dT%H:%M:%S'), 
            end_date=end_date_tmp.strftime('%Y-%m-%dT%H:%M:%S'),
            type_filter='W', 
            return_count=True,
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
     
        nb_updates_other_time_periods[-1] += number_of_withdrawals
        
output = {
    "time": time,
    "size": size,
    "final_answer": "Yes" if nb_updates_targeted_time_period > 2*np.mean(nb_updates_other_time_periods) else "No",
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)