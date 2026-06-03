from pyXoXapi import *
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import json

question_id = 13
set_id = 2


answer_file = f"../../evaluation/eval_results/XoX/answer{question_id}.json"

size = 0
time = 0

final_answer = None

end_date = datetime.combine(
    datetime.today().date(),
    datetime.min.time()
)

start_date = end_date - relativedelta(months=1)

current_date = end_date

selected_vantage_points = get_vantage_points(
    vp_ips=['2001:13c7:7020:300::254', '2001:7f8::8463:0:1', '2001:43f8:6d0::2934', '208.115.136.119', '206.126.110.5', '80.81.192.79', '80.81.194.45', '203.159.68.69', '203.181.248.195', '2a14:7580:9011::'],
    data_afi=None,
)

while current_date > start_date:

    connected = False

    for vantage_point in selected_vantage_points:

        rib_data = get_rib(
            [vantage_point],
            date=current_date.strftime('%Y-%m-%dT%H:%M:%S'),
            return_community=False,
            aspath_regexp='(^| )46887 6461($| )|(^| )6461 46887($| )',
            return_count=True,
            details=True,
        )

        bgp_data = rib_data.get("data", {}).get("bgp", {})
        time_info = rib_data.get("seconds", 0)
        size_info = rib_data.get("bytes", 0)

        size += size_info
        time += time_info

        if bgp_data.get(str(vantage_point.unique_id), 0) > 0:
            connected = True
            final_answer = {
                "status": "connected",
                "date": None
            }
            break

    if not connected:
        final_answer = {
            "status": "disconnected",
            "date": current_date.strftime('%Y-%m-%dT%H:%M:%S')
        }
        break

    current_date = current_date - timedelta(days=1)

output = {
    "time": time,
    "size": size,
    "final_answer": final_answer,
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)