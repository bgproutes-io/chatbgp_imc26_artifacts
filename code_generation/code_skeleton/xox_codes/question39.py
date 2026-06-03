from pyXoXapi import *
import os
import json
from datetime import datetime

question_id = 39
set_id = 2


answer_file = f"../../evaluation/eval_results/XoX/answer{question_id}.json"

time = 0
size = 0
final_answer = []

community_set = set()

selected_vantage_points = get_vantage_points(
    vp_ips=['2001:13c7:7020:300::254', '2001:7f8::8463:0:1', '2001:43f8:6d0::2934', '208.115.136.119', '206.126.110.5', '80.81.192.79', '80.81.194.45', '203.159.68.69', '203.181.248.195', '2a14:7580:9011::'],
)

for vantage_point in selected_vantage_points:

    rib_data = get_rib(
        [vantage_point],
        date="2026-05-20T00:00:00",
        return_community=True,
        return_aspath=False,
        prefix_exact_match=["2001:559:8633::/48"],
        details=True,
    )

    bgp_data = rib_data.get("data", {}).get("bgp", {})
    time_info = rib_data.get("seconds", 0)
    size_info = rib_data.get("bytes", 0)

    time += time_info or 0
    size += size_info or 0

    for vp_id, prefix_data in bgp_data.items():

        if not prefix_data:
            continue

        for prefix, entry in prefix_data.items():

            if len(entry) < 2:
                continue

            community_str = entry[1]

            if not community_str:
                continue

            communities = community_str.split()

            for community in communities:
                community_set.add(community)

final_answer = sorted(list(community_set))

output = {
    "time": time,
    "size": size,
    "final_answer": final_answer,
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)