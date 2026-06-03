from pyXoXapi import *
import os
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


answer_file = "../../evaluation/eval_results/OP/answer12.json"

size = 0
time = 0
bgp2go = set()
results = []

end_date = datetime.combine(
    datetime.today().date(),
    datetime.min.time()
)

start_date = end_date - relativedelta(months=1)

selected_vantage_points = get_vantage_points(
    vp_ips=param_vp,
    data_afi=param_ip_protocol,
)

for vantage_point in selected_vantage_points:

    current_date = end_date

    found = False

    while current_date > start_date and not found:

        prev_day = max(
            current_date - timedelta(days=1),
            start_date
        )

        update_data = get_updates(
            [vantage_point],
            return_community=False,
            return_aspath=False,
            start_date=prev_day.strftime('%Y-%m-%dT%H:%M:%S'),
            end_date=current_date.strftime('%Y-%m-%dT%H:%M:%S'),
            prefix_exact_match=[param_prefix],
            chronological_order=False,
            max_updates_to_return=1,
            details=True,
        )

        bgp_updates = update_data.get("data", {}).get("bgp", {})
        time_info = update_data.get("seconds", 0)
        size_info = update_data.get("bytes", 0)

        size += size_info
        time += time_info

        for vp_id, update_entries in bgp_updates.items():

            if not update_entries:
                continue
            
            bgp2go.add(vantage_point.ip)

            last_time = update_entries[0][0]

            results.append({
                'vp': str(vantage_point.unique_id),
                'last_time': last_time,
            })

            found = True
            break

        current_date = prev_day

output = {
    "time": time,
    "size": size,
    "final_answer": results,
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)