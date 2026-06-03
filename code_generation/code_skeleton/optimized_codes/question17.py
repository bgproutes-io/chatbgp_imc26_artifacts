from pyXoXapi import *
import os
import json
from datetime import datetime, timedelta


answer_file = "../../evaluation/eval_results/OP/answer17.json"
size = 0
time = 0

hourly_totals = []
bgp2go = set()
selected_vantage_points = get_vantage_points(
    vp_ips=param_vp, 
    ) 

start_of_day = datetime.strptime(
    param_time_interval_start,
    "%Y-%m-%dT%H:%M:%S"
)

end_of_day = datetime.strptime(
    param_time_interval_end,
    "%Y-%m-%dT%H:%M:%S"
)

total_hours = int(
    (end_of_day - start_of_day).total_seconds() / 3600
) + 1

for hour in range(total_hours):
    hour_start = start_of_day + timedelta(hours=hour)
    hour_end = hour_start + timedelta(hours=1) - timedelta(seconds=1)

    hour_key = hour_start.strftime("%Y-%m-%d %H:00:00")

    for vantage_point in selected_vantage_points:
        update_data = get_updates(
            [vantage_point],
            return_community = False,
            return_aspath = False,
            start_date=hour_start.strftime("%Y-%m-%dT%H:%M:%S"),
            end_date=hour_end.strftime("%Y-%m-%dT%H:%M:%S"),
            return_count=True,
            type_filter = 'A',
            details = True,
            ) 

        bgp_updates = update_data.get("data", {}).get("bgp", {})
        time_info = update_data.get("seconds")
        size_info = update_data.get("bytes")
    
        size += size_info or 0
        time += time_info or 0
    
        for vp_id, counts in bgp_updates.items():
            
            announcements = counts.get("A", 0)
            
            bgp2go.add(vantage_point.ip)

            hourly_totals.append({
                "vp": str(vantage_point.unique_id),
                "hour": hour_key,
                'count': announcements
            })
                      
output = {
    "time": time,
    "size": size,
    "final_answer": hourly_totals,
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)