from pyXoXapi import *
import os
import json
import ipaddress
from datetime import datetime

question_id = 27
set_id = 2


answer_file = f"../../evaluation/eval_results/XoX/answer{question_id}.json"

size = 0
time = 0

bogon_prefixes = set()

selected_vantage_points = get_vantage_points(
    vp_ips=['2001:13c7:7020:300::254', '2001:7f8::8463:0:1', '2001:43f8:6d0::2934', '208.115.136.119', '206.126.110.5', '80.81.192.79', '80.81.194.45', '203.159.68.69', '203.181.248.195', '2a14:7580:9011::'],
    data_afi=None,
)

# Common IPv4 and IPv6 bogon/reserved ranges.
bogon_networks = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("ff00::/8"),
    ipaddress.ip_network("2001:db8::/32"),
]

for vantage_point in selected_vantage_points:

    rib_data = get_rib(
        [vantage_point],
        date="2026-05-20T00:00:00",
        aspath_regexp=r'(^| )206216$',
        return_community=False,
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

        for prefix in prefix_data.keys():

            try:
                network = ipaddress.ip_network(prefix, strict=False)
            except Exception:
                continue

            for bogon in bogon_networks:

                if network.version != bogon.version:
                    continue

                if network.subnet_of(bogon) or bogon.subnet_of(network):
                    bogon_prefixes.add(prefix)
                    break

output = {
    "time": time,
    "size": size,
    "final_answer": len(bogon_prefixes),
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)