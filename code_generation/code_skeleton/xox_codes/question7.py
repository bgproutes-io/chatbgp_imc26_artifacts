from pyXoXapi import *
import networkx as nx
import os
import json
from datetime import datetime

question_id = 7
set_id = 2


answer_file = f"../../evaluation/eval_results/XoX/answer{question_id}.json"

time = 0
size = 0
final_answer = []

target_as = 16509

AS_topology = nx.Graph()
middle_ases = set()
edge_ases = set()

selected_vantage_points = get_vantage_points(
    vp_ips=['2001:13c7:7020:300::254', '2001:7f8::8463:0:1', '2001:43f8:6d0::2934', '208.115.136.119', '206.126.110.5', '80.81.192.79', '80.81.194.45', '203.159.68.69', '203.181.248.195', '2a14:7580:9011::'],
    data_afi=None,
)

for vantage_point in selected_vantage_points:

    rib_data = get_rib(
        [vantage_point],
        date="2026-05-20T00:00:00",
        return_community=False,
        aspath_regexp='(^| )' + str(target_as) + '( |$)',
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

            as_path = entry[0]

            if not as_path:
                continue

            asns = [int(asn) for asn in as_path.split() if asn.isdigit()]

            if len(asns) == 0:
                continue

            edge_ases.add(asns[0])
            edge_ases.add(asns[-1])

            for asn in asns[1:-1]:
                middle_ases.add(asn)

            for i in range(len(asns) - 1):
                AS_topology.add_edge(asns[i], asns[i + 1])

neighbors_only_middle = []

if target_as in AS_topology:

    for neighbor in AS_topology.neighbors(target_as):

        if neighbor in middle_ases and neighbor not in edge_ases:
            neighbors_only_middle.append(neighbor)

final_answer = sorted(neighbors_only_middle)

output = {
    "time": time,
    "size": size,
    "final_answer": final_answer,
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)