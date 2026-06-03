from pyXoXapi import *
import os
import json
from datetime import datetime

question_id = 19
set_id = 2


answer_file = f"../../evaluation/eval_results/XoX/answer{question_id}.json"

size = 0
time = 0

desired_updates = []

community_regex = (
    "(^| )(60326:110|55095:63301|2152:65437)( |$)"
)

selected_vantage_points = get_vantage_points(
    vp_ips=['2001:13c7:7020:300::254', '2001:7f8::8463:0:1', '2001:43f8:6d0::2934', '208.115.136.119', '206.126.110.5', '80.81.192.79', '80.81.194.45', '203.159.68.69', '203.181.248.195', '2a14:7580:9011::'],
    data_afi=None,
)

for vantage_point in selected_vantage_points:

    update_data = get_updates(
        [vantage_point],
        start_date="2026-05-20T00:00:00",
        end_date="2026-05-20T23:59:59",
        return_community=True,
        community_regexp=community_regex,
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

        for update in update_entries:
            desired_updates.append(update)

output = {
    "time": time,
    "size": size,
    "final_answer": desired_updates,
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)