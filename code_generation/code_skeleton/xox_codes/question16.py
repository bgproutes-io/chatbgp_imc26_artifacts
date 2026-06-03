from pyXoXapi import *
import os
import json

question_id = 16
set_id = 2


answer_file = f"../../evaluation/eval_results/XoX/answer{question_id}.json"

size = 0
time = 0

vp_and_nb_updates_tuple = []

selected_vantage_points = get_vantage_points(
    vp_ips=['2001:13c7:7020:300::254', '2001:7f8::8463:0:1', '2001:43f8:6d0::2934', '208.115.136.119', '206.126.110.5', '80.81.192.79', '80.81.194.45', '203.159.68.69', '203.181.248.195', '2a14:7580:9011::'],
)

for vantage_point in selected_vantage_points:

    update_data = get_updates(
        [vantage_point],
        return_community=False,
        return_aspath=False,
        start_date="2026-05-20T00:00:00",
        end_date="2026-05-20T23:59:59",
        return_count=True,
        details=True,
    )

    bgp_updates = update_data.get("data", {}).get("bgp", {})
    time_info = update_data.get("seconds", 0)
    size_info = update_data.get("bytes", 0)

    size += size_info
    time += time_info

    vp_updates = bgp_updates.get(str(vantage_point.unique_id))

    if vp_updates is None:
        continue

    number_of_withdrawals = vp_updates.get("W", 0)
    number_of_announcements = vp_updates.get("A", 0)

    number_of_updates = (
        number_of_announcements + number_of_withdrawals
    )

    vp_and_nb_updates_tuple.append({
        "vp": str(vantage_point.unique_id),
        "updates": number_of_updates
    })

final_answer = sorted(
    vp_and_nb_updates_tuple,
    key=lambda x: x["updates"],
    reverse=True
)

output = {
    "time": time,
    "size": size,
    "final_answer": final_answer,
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)