from pyXoXapi import *
import os
import json
from datetime import datetime


answer_file = "../../evaluation/eval_results/OP/answer35.json"
size = 0
time = 0

total_paths = 0
matching_paths = 0
bgp2go = set()
selected_vantage_points = get_vantage_points(
    vp_ips=param_vp, 
    data_afi = param_ip_protocol,
    ) 

for vantage_point in selected_vantage_points:
    
    rib_param_asx_to_param_asy = get_rib(
        [vantage_point], 
        date = param_time, 
        return_community = False,
        aspath_regexp='(^| )'+str(param_asx)+' (|.* )'+str(param_asy)+'($| )',
        details = True,
        ) 
    
    rib_param_asy_to_param_asx = get_rib(
        [vantage_point], 
        date = param_time, 
        return_community = False,
        aspath_regexp='(^| )'+str(param_asy)+' (|.* )'+str(param_asx)+'($| )',
        details = True,
        ) 
    
    bgp_param_asx_to_asy_data = rib_param_asx_to_param_asy.get("data", {}).get("bgp", {})
    time_info_x = rib_param_asx_to_param_asy.get("seconds")
    size_info_x = rib_param_asx_to_param_asy.get("bytes")
    
    size += size_info_x or 0
    time += time_info_x or 0
    
    bgp_param_asy_to_asx_data = rib_param_asy_to_param_asx.get("data", {}).get("bgp", {})
    time_info_y = rib_param_asy_to_param_asx.get("seconds")
    size_info_y = rib_param_asy_to_param_asx.get("bytes")
    
    size += size_info_y or 0
    time += time_info_y or 0
    
    for vp_id, prefix_asx_to_asy_data in bgp_param_asx_to_asy_data.items():
        if not prefix_asx_to_asy_data:
            continue
        
        bgp2go.add(vantage_point.ip)
        for prefix, entry in prefix_asx_to_asy_data.items():

            aspath_param_asx_to_param_asy = entry[0]
            if not aspath_param_asx_to_param_asy:
                continue
            
            total_paths+=1
            
            asns_param_asx_to_param_asy = [int(asn) for asn in aspath_param_asx_to_param_asy.split() if asn.isdigit()]
            
            sub_aspath_param_asx_to_param_asy = asns_param_asx_to_param_asy[asns_param_asx_to_param_asy.index(int(param_asx)):asns_param_asx_to_param_asy.index(int(param_asy))+1]
            
            found_match = False
    
            for vp_id, prefix_asy_to_asx_data in bgp_param_asy_to_asx_data.items():
                if not prefix_asy_to_asx_data:
                    continue
                
                bgp2go.add(vantage_point.ip)

                for prefix, entry in prefix_asy_to_asx_data.items():
                    
                    aspath_param_asy_to_param_asx = entry[0]
                    if not aspath_param_asy_to_param_asx:
                        continue
                    
                    asns_param_asy_to_param_asx = [int(asn) for asn in aspath_param_asy_to_param_asx.split() if asn.isdigit()]
                    
                    sub_aspath_param_asy_to_param_asx = asns_param_asy_to_param_asx[asns_param_asy_to_param_asx.index(int(param_asy)):asns_param_asy_to_param_asx.index(int(param_asx))+1]
                    
                    if sub_aspath_param_asx_to_param_asy == sub_aspath_param_asy_to_param_asx[::-1]:
                        found_match = True
                        matching_paths += 1
                        break
                    
                if found_match:
                    break
                
if total_paths > 0:
    proportion = matching_paths / total_paths
else:
    proportion = 0

output = {
    "time": time,
    "size": size,
    "final_answer": proportion,
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)
            