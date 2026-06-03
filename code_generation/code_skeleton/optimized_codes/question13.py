from pyXoXapi import *
from datetime import datetime, timedelta
import os
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


answer_file = "../../evaluation/eval_results/OP/answer13.json"

size = 0
time = 0
result = None
bgp2go = set()
end_date = datetime.combine(
    datetime.today().date(),
    datetime.min.time()
)
start_date = end_date - relativedelta(months=1)

current_date = end_date

selected_vantage_points = get_vantage_points(
    vp_ips=param_vp,
    data_afi=param_ip_protocol,
)

while current_date > start_date:

    connected = False

    for vantage_point in selected_vantage_points:

        number_of_entries = get_rib(
            [vantage_point], 
            date = current_date.strftime('%Y-%m-%dT%H:%M:%S'), 
            return_community = False,
            aspath_regexp='(^| )'+str(param_asx)+' '+str(param_asy)+'($| )|(^| )'+str(param_asy)+' '+str(param_asx)+'($| )',
            return_count=True,
            details = True,
        ) 

        bgp_data = number_of_entries.get("data", {}).get("bgp", {})
        time_info = number_of_entries.get("seconds")
        size_info = number_of_entries.get("bytes")
    
        size += size_info or 0
        time += time_info or 0
        if bgp_data.get(str(vantage_point.unique_id),0) > 0:
            bgp2go.add(vantage_point.ip)
            connected = True
            result = {
                'status': "connected",
                'date': None
            }
            break
        
    if not connected:
        print (current_date)
        result = {
                'status': "disconnected",
                'date': current_date.strftime('%Y-%m-%dT%H:%M:%S')
            }
        break
    
    current_date = current_date - timedelta(days=1)
    
output = {
    "time": time,
    "size": size,
    "final_answer": result,
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)