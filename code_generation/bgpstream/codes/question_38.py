# What is the percentage of single hop AS paths (i.e. two ASes, one hop) observed on 3/1/24 at 15:21:05 from peers 143.192.143.111, 50.188.246.246, 103.52.15.204, and 238:81a9:96a4:2939:bac2:87e7:251b:d58d for IPv6?

#!/usr/bin/env python

import pybgpstream

TIME_FROM = "2024-03-01 15:21:05"
TIME_UNTIL = "2024-03-01 15:21:05"

VPS = {
    "143.192.143.111",
    "50.188.246.246",
    "103.52.15.204",
    "238:81a9:96a4:2939:bac2:87e7:251b:d58d",
}

stream = pybgpstream.BGPStream(
    from_time=TIME_FROM,
    until_time=TIME_UNTIL,
    record_type="ribs",
    filter="ipversion 6"
)

total = 0
single_hop = 0

for rec in stream.records():
    for elem in rec:
        if elem.peer_address not in VPS:
            continue

        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        ases = aspath.split()
        if len(ases) < 2:
            continue

        total += 1
        if len(ases) == 2:
            single_hop += 1

if total == 0:
    print("No AS paths observed.")
else:
    pct = 100 * single_hop / total
    print("Total IPv6 AS paths:", total)
    print("Single-hop AS paths:", single_hop)
    print("Percentage:", pct)
