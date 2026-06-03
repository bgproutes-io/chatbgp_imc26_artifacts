from pyXoXapi import *
import os
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

question_id = 11
set_id = 2


answer_file = f"../../evaluation/eval_results/XoX/answer{question_id}.json"

time = 0
size = 0
final_answer = None

target_edge_1 = 7922
target_edge_2 = 2152

end_date = datetime.combine(
    datetime.today().date(),
    datetime.min.time()
)

start_date = end_date - relativedelta(months=1)

selected_vantage_points = get_vantage_points(
    vp_ips=['2001:13c7:7020:300::254', '2001:7f8::8463:0:1', '2001:43f8:6d0::2934', '208.115.136.119', '206.126.110.5', '80.81.192.79', '80.81.194.45', '203.159.68.69', '203.181.248.195', '2a14:7580:9011::'],
    data_afi=6,
)

first_seen_timestamp = None

current_date = start_date

while current_date < end_date:

    next_date = min(current_date + timedelta(days=1), end_date)

    found = False

    for vantage_point in selected_vantage_points:

        rib_data = get_rib(
            [vantage_point],
            date=current_date.strftime('%Y-%m-%dT%H:%M:%S'),
            return_community=False,
            aspath_regexp=(
                '(^| )' + str(target_edge_1) + ' ' + str(target_edge_2) + '( |$)'
                + '|(^| )' + str(target_edge_2) + ' ' + str(target_edge_1) + '( |$)'
            ),
            details=True,
        )

        bgp_data = rib_data.get("data", {}).get("bgp", {})
        time_info = rib_data.get("seconds", 0)
        size_info = rib_data.get("bytes", 0)

        time += time_info or 0
        size += size_info or 0

        for vp_id, prefix_data in bgp_data.items():

            if prefix_data:
                first_seen_timestamp = int(current_date.timestamp())
                found = True
                break

        if found:
            break

    if found:
        break

    current_date = next_date

final_answer = first_seen_timestamp

output = {
    "time": time,
    "size": size,
    "final_answer": final_answer,
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)