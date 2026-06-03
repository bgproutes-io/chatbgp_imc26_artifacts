from pyXoXapi import *
import os
import json
from datetime import datetime, timedelta


question_id = 36
set_id = 2

answer_file = f"../../evaluation/eval_results/XoX/answer{question_id}.json"

size = 0
time = 0

results = []

selected_vantage_points = get_vantage_points(
    vp_ips=['2001:13c7:7020:300::254', '2001:7f8::8463:0:1', '2001:43f8:6d0::2934', '208.115.136.119', '206.126.110.5', '80.81.192.79', '80.81.194.45', '203.159.68.69', '203.181.248.195', '2a14:7580:9011::'],
    data_afi=None,
)

start_date = "2026-05-20T00:00:00"
end_date = "2026-05-20T23:59:59"

for vantage_point in selected_vantage_points:

    links_start = set()
    links_end = set()

    rib_start = get_rib(
        [vantage_point],
        date=start_date,
        return_community=False,
        details=True,
    )

    bgp_data_start = rib_start.get("data", {}).get("bgp", {})
    time_info = rib_start.get("seconds", 0)
    size_info = rib_start.get("bytes", 0)

    size += size_info
    time += time_info

    for vp_id, prefix_data in bgp_data_start.items():

        if not prefix_data:
            continue

        for prefix, entry in prefix_data.items():

            as_path = entry[0]

            if not as_path:
                continue

            asns = [asn for asn in as_path.split() if asn.isdigit()]

            for i in range(len(asns) - 1):
                links_start.add((asns[i], asns[i + 1]))

    rib_end = get_rib(
        [vantage_point],
        date=end_date,
        return_community=False,
        details=True,
    )

    bgp_data_end = rib_end.get("data", {}).get("bgp", {})
    time_info = rib_end.get("seconds", 0)
    size_info = rib_end.get("bytes", 0)

    size += size_info
    time += time_info

    for vp_id, prefix_data in bgp_data_end.items():

        if not prefix_data:
            continue

        for prefix, entry in prefix_data.items():

            as_path = entry[0]

            if not as_path:
                continue

            asns = [asn for asn in as_path.split() if asn.isdigit()]

            for i in range(len(asns) - 1):
                links_end.add((asns[i], asns[i + 1]))

    start_count = len(links_start)
    end_count = len(links_end)

    if start_count > 0:
        increase_pct = ((end_count - start_count) / start_count) * 100
    else:
        increase_pct = 0

    results.append({
        "vp": str(vantage_point.unique_id),
        "increase_pct": increase_pct
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