from pyXoXapi import *
import os
import json
from datetime import datetime


answer_file = "../../evaluation/eval_results/OP/answer5.json"

size = 0
time = 0

shortest_distance = None
bgp2go = set()
selected_vantage_points = get_vantage_points(
    vp_ips=param_vp, 
    data_afi = param_ip_protocol,
    ) 

for vantage_point in selected_vantage_points:

    rib_data = get_rib(
        [vantage_point], 
        date = param_time, 
        return_community = False,
        aspath_regexp ='(^| )'+str(param_asx)+' (|.* )'+str(param_asy)+'($| )|(^| )'+str(param_asy)+' (|.* )'+str(param_asx)+'($| )',
        details = True,
        ) 

    bgp_data = rib_data.get("data", {}).get("bgp", {})
    time_info = rib_data.get("seconds")
    size_info = rib_data.get("bytes")
    
    size += size_info or 0
    time += time_info or 0
    
    for vp_id, prefix_data in bgp_data.items():

        for prefix, entry in prefix_data.items():
       
            as_path = entry[0]
            if not as_path:
                continue
            
            bgp2go.add(vantage_point.ip)
            asns = [int(asn) for asn in as_path.split() if asn.isdigit()]
            
            index_ASX = None
            index_ASY = None

            for index in range(0, len(asns)):
                if int(param_asx) == asns[index]:
                    index_ASX = index
                if int(param_asy) == asns[index]:
                    index_ASY = index
                    
            if index_ASX is not None and index_ASY is not None:    
  
                if shortest_distance is None:
                    shortest_distance = abs(index_ASX-index_ASY)

                elif abs(index_ASX-index_ASY) < shortest_distance:
                    shortest_distance = abs(index_ASX-index_ASY)

output = {
    "time": time,
    "size": size,
    "final_answer": shortest_distance,
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)
