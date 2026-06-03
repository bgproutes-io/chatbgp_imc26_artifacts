from pyXoXapi import *
from datetime import datetime, timedelta
import numpy as np
import os
import json

question_id = 15
set_id = 2


answer_file = f"../../evaluation/eval_results/XoX/answer{question_id}.json"

size = 0
time = 0

target_withdrawals = 0
historical_withdrawals = []

selected_vantage_points = get_vantage_points(
    vp_ips=['2001:13c7:7020:300::254', '2001:7f8::8463:0:1', '2001:43f8:6d0::2934', '208.115.136.119', '206.126.110.5', '80.81.192.79', '80.81.194.45', '203.159.68.69', '203.181.248.195', '2a14:7580:9011::'],
)

for vantage_point in selected_vantage_points:

    update_data = get_updates(
        [vantage_point],
        return_aspath=False,
        return_community=False,
        start_date="2026-05-20T00:00:00",
        end_date="2026-05-20T23:59:59",
        type_filter='W',
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

    target_withdrawals += vp_updates.get("W", 0)

for period_shift_day in range(1, 11):

    start_date_tmp = (
        datetime.strptime("2026-05-20T00:00:00", "%Y-%m-%dT%H:%M:%S")
        - timedelta(days=period_shift_day)
    )

    end_date_tmp = (
        datetime.strptime("2026-05-20T23:59:59", "%Y-%m-%dT%H:%M:%S")
        - timedelta(days=period_shift_day)
    )

    interval_withdrawals = 0

    for vantage_point in selected_vantage_points:

        update_data = get_updates(
            [vantage_point],
            return_aspath=False,
            return_community=False,
            start_date=start_date_tmp.strftime("%Y-%m-%dT%H:%M:%S"),
            end_date=end_date_tmp.strftime("%Y-%m-%dT%H:%M:%S"),
            type_filter='W',
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

        interval_withdrawals += vp_updates.get("W", 0)

    historical_withdrawals.append(interval_withdrawals)

historical_average = (
    np.mean(historical_withdrawals)
    if historical_withdrawals
    else 0
)

final_answer = (
    "Yes"
    if target_withdrawals >= 2 * historical_average
    else "No"
)

output = {
    "time": time,
    "size": size,
    "final_answer": final_answer,
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)