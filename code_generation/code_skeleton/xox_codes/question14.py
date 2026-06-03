from pyXoXapi import *
import os
import json

question_id = 14
set_id = 2


answer_file = f"../../evaluation/eval_results/XoX/answer{question_id}.json"

size = 0
time = 0

origin_ases = set()

selected_vantage_points = get_vantage_points(
    vp_ips=['2001:13c7:7020:300::254', '2001:7f8::8463:0:1', '2001:43f8:6d0::2934', '208.115.136.119', '206.126.110.5', '80.81.192.79', '80.81.194.45', '203.159.68.69', '203.181.248.195', '2a14:7580:9011::'],
)

for vantage_point in selected_vantage_points:

    update_data = get_updates(
        [vantage_point],
        return_community=False,
        start_date="2026-05-20T00:00:00",
        end_date="2026-05-20T23:59:59",
        prefix_exact_match=["2001:559:8633::/48"],
        type_filter='A',
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

            as_path = update[3]

            if not as_path:
                continue

            asns = [int(asn) for asn in as_path.split() if asn.isdigit()]

            if len(asns) == 0:
                continue

            origin_ases.add(asns[-1])

            if len(origin_ases) > 1:
                break

        if len(origin_ases) > 1:
            break

    if len(origin_ases) > 1:
        break

final_answer = "Yes" if len(origin_ases) > 1 else "No"

output = {
    "time": time,
    "size": size,
    "final_answer": final_answer,
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)