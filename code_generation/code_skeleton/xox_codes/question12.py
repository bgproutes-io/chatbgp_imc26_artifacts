from pyXoXapi import *
import os
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

question_id = 12
set_id = 2


answer_file = f"../../evaluation/eval_results/XoX/answer{question_id}.json"

time = 0
size = 0
final_answer = []

results = []

end_date = datetime.combine(
    datetime.today().date(),
    datetime.min.time()
)

start_date = end_date - relativedelta(months=1)

selected_vantage_points = get_vantage_points(
    vp_ips=['2001:13c7:7020:300::254', '2001:7f8::8463:0:1', '2001:43f8:6d0::2934', '208.115.136.119', '206.126.110.5', '80.81.192.79', '80.81.194.45', '203.159.68.69', '203.181.248.195', '2a14:7580:9011::'],
    data_afi=None,
)

for vantage_point in selected_vantage_points:

    latest_timestamp = None
    current_date = end_date

    while current_date > start_date:

        prev_day = max(current_date - timedelta(days=1), start_date)

        update_data = get_updates(
            [vantage_point],
            return_community=False,
            return_aspath=False,
            start_date=prev_day.strftime('%Y-%m-%dT%H:%M:%S'),
            end_date=current_date.strftime('%Y-%m-%dT%H:%M:%S'),
            prefix_exact_match=["2a14:3f87:9800::/38"],
            chronological_order=False,
            max_updates_to_return=1,
            details=True,
        )

        bgp_updates = update_data.get("data", {}).get("bgp", {})
        time_info = update_data.get("seconds", 0)
        size_info = update_data.get("bytes", 0)

        time += time_info or 0
        size += size_info or 0

        found = False

        for vp_id, update_entries in bgp_updates.items():

            if not update_entries:
                continue

            latest_timestamp = update_entries[0][0]
            found = True
            break

        if found:
            break

        current_date = prev_day

    results.append({
        'vp': str(vantage_point.unique_id),
        'last_time': latest_timestamp
    })

final_answer = results

output = {
    "time": time,
    "size": size,
    "final_answer": final_answer,
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)