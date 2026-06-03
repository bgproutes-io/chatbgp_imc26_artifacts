from pyXoXapi import *
import os
import json
from datetime import datetime, timedelta

question_id = 17
set_id = 2


answer_file = f"../../evaluation/eval_results/XoX/answer{question_id}.json"

time = 0
size = 0
final_answer = []

results = []

selected_vantage_points = get_vantage_points(
    vp_ips=['2001:13c7:7020:300::254', '2001:7f8::8463:0:1', '2001:43f8:6d0::2934', '208.115.136.119', '206.126.110.5', '80.81.192.79', '80.81.194.45', '203.159.68.69', '203.181.248.195', '2a14:7580:9011::'],
)

start_datetime = datetime.strptime(
    "2026-05-20T00:00:00",
    "%Y-%m-%dT%H:%M:%S"
)

end_datetime = datetime.strptime(
    "2026-05-20T23:59:59",
    "%Y-%m-%dT%H:%M:%S"
)

current_hour = start_datetime

while current_hour <= end_datetime:

    next_hour = min(current_hour + timedelta(hours=1), end_datetime)

    for vantage_point in selected_vantage_points:

        update_data = get_updates(
            [vantage_point],
            start_date=current_hour.strftime("%Y-%m-%dT%H:%M:%S"),
            end_date=next_hour.strftime("%Y-%m-%dT%H:%M:%S"),
            return_count=True,
            type_filter='A',
            return_aspath=False,
            return_community=False,
            details=True,
        )

        bgp_updates = update_data.get("data", {}).get("bgp", {})
        time_info = update_data.get("seconds", 0)
        size_info = update_data.get("bytes", 0)

        time += time_info or 0
        size += size_info or 0

        vp_updates = bgp_updates.get(str(vantage_point.unique_id), {})

        announcement_count = vp_updates.get("A", 0)

        results.append({
            'vp': str(vantage_point.unique_id),
            'hour': current_hour.strftime("%Y-%m-%d %H:00:00"),
            'count': announcement_count
        })

    current_hour += timedelta(hours=1)

final_answer = results

output = {
    "time": time,
    "size": size,
    "final_answer": final_answer,
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)