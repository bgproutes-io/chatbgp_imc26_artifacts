from pyXoXapi import *
import os
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

question_id = 10
set_id = 2


answer_file = f"../../evaluation/eval_results/XoX/answer{question_id}.json"

size = 0
time = 0

first_update_observed_time = None

end_date = datetime.combine(
    datetime.today().date(),
    datetime.min.time()
)

start_date = end_date - relativedelta(months=1)

current_date = start_date

selected_vantage_points = get_vantage_points(
    vp_ips=['2001:13c7:7020:300::254', '2001:7f8::8463:0:1', '2001:43f8:6d0::2934', '208.115.136.119', '206.126.110.5', '80.81.192.79', '80.81.194.45', '203.159.68.69', '203.181.248.195', '2a14:7580:9011::'],
    data_afi=None,
)

while current_date < end_date:

    next_day = min(current_date + timedelta(days=1), end_date)

    for vantage_point in selected_vantage_points:

        update_data = get_updates(
            [vantage_point],
            return_community=False,
            start_date=current_date.strftime('%Y-%m-%dT%H:%M:%S'),
            end_date=next_day.strftime('%Y-%m-%dT%H:%M:%S'),
            aspath_regexp='(^| )' + str(8849) + '( |$)',
            chronological_order=True,
            max_updates_to_return=1,
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

            first_time = update_entries[0][0]

            if (
                first_update_observed_time is None
                or first_time < first_update_observed_time
            ):
                first_update_observed_time = first_time

    current_date = next_day

output = {
    "time": time,
    "size": size,
    "final_answer": first_update_observed_time,
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)