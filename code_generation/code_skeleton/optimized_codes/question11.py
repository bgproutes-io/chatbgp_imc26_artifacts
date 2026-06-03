from pyXoXapi import *
import os
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


answer_file = "../../evaluation/eval_results/OP/answer11.json"

size = 0
time = 0
bgp2go = set()

end_date = datetime.combine(
    datetime.today().date(),
    datetime.min.time()
)

start_date = end_date - relativedelta(months=1)

current_date = start_date
first_update_observed_time = None
earliest_day_found = None

selected_vantage_points = get_vantage_points(
    vp_ips=param_vp,
    data_afi=param_ip_protocol,
)

while current_date < end_date:

    if (
        earliest_day_found is not None
        and current_date.date() > earliest_day_found
    ):
        break

    next_day = min(current_date + timedelta(days=1), end_date)

    for vantage_point in selected_vantage_points:

        update_data = get_updates(
            [vantage_point],
            return_community=False,
            start_date=current_date.strftime('%Y-%m-%dT%H:%M:%S'),
            end_date=next_day.strftime('%Y-%m-%dT%H:%M:%S'),
            aspath_regexp='(^| )'+str(param_asx)+' '+str(param_asy)+'($| )|(^| )'+str(param_asy)+' '+str(param_asx)+'($| )',
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

            bgp2go.add(vantage_point.ip)

            first_time = update_entries[0][0]

            if (
                first_update_observed_time is None
                or first_time < first_update_observed_time
            ):
                first_update_observed_time = first_time

                earliest_day_found = datetime.fromtimestamp(
                    first_time
                ).date()

    current_date = next_day

output = {
    "time": time,
    "size": size,
    "final_answer": first_update_observed_time,
    "bgp2go": list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)