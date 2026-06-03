from pyXoXapi import *
import os
import json
from datetime import datetime


answer_file = "../../evaluation/eval_results/OP/answer36.json"
time = 0
size = 0
bgp2go = set()
def get_as_links_vantage_point(vantage_point, date):
    global size, time, bgp2go
    
    as_links = set()
    rib_data = get_rib(
        [vantage_point], 
        date = date, 
        return_community = False,
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

        for prefix, entry in prefix_data.items():

            as_path = entry[0]
            if not as_path:
                continue
            
            bgp2go.add(vantage_point.ip)
            asns = [int(asn) for asn in as_path.split() if asn.isdigit()]
            
            if len(asns) == 0:
                continue
            
            for i in range(len(asns) - 1):
            
                as_links.add((asns[i], asns[i+1]))

    return as_links

selected_vantage_points = get_vantage_points(
    vp_ips=param_vp,
)

result = []
for vantage_point in selected_vantage_points:

    start_as_links = get_as_links_vantage_point(vantage_point, param_time_interval_start)
    end_as_links = get_as_links_vantage_point(vantage_point, param_time_interval_end)

    as_links_increase = (len(end_as_links) - len(start_as_links)) / len(start_as_links) if len(start_as_links) > 0 else 0

    result.append({
    "vp": str(vantage_point.unique_id),
    "increase_pct": as_links_increase * 100
})

output = {
    "time": time,
    "size": size,
    "final_answer": result,
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)
            