from pyXoXapi import *
import os
import json

question_id = 5
set_id = 2


answer_file = f"../../evaluation/eval_results/XoX/answer{question_id}.json"

size = 0
time = 0

source_as = 11164
target_as = 3491

shortest_distance = None

selected_vantage_points = get_vantage_points(
    vp_ips=['2001:13c7:7020:300::254', '2001:7f8::8463:0:1', '2001:43f8:6d0::2934', '208.115.136.119', '206.126.110.5', '80.81.192.79', '80.81.194.45', '203.159.68.69', '203.181.248.195', '2a14:7580:9011::'],
    data_afi=None,
)

for vantage_point in selected_vantage_points:

    rib_data = get_rib(
        [vantage_point],
        date="2026-05-20T00:00:00",
        return_community=False,
        aspath_regexp='(^| )' + str(source_as) + '( |$).*' + str(target_as) + '( |$)|(^| )' + str(target_as) + '( |$).*' + str(source_as) + '( |$)',
        details=True,
    )

    bgp_data = rib_data.get("data", {}).get("bgp", {})
    time_info = rib_data.get("seconds", 0)
    size_info = rib_data.get("bytes", 0)

    size += size_info
    time += time_info

    for vp_id, prefix_data in bgp_data.items():

        if not prefix_data:
            continue

        for prefix, entry in prefix_data.items():

            as_path = entry[0]

            if not as_path:
                continue

            asns = [int(asn) for asn in as_path.split() if asn.isdigit()]

            positions_source = [
                idx for idx, asn in enumerate(asns)
                if asn == source_as
            ]

            positions_target = [
                idx for idx, asn in enumerate(asns)
                if asn == target_as
            ]

            for pos_source in positions_source:
                for pos_target in positions_target:

                    hop_distance = abs(pos_source - pos_target)

                    if (
                        shortest_distance is None
                        or hop_distance < shortest_distance
                    ):
                        shortest_distance = hop_distance

output = {
    "time": time,
    "size": size,
    "final_answer": shortest_distance,
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)