# What is the average length of an AS path in the routing table when combining VPs with the IP addresses 143.192.143.111, 238:81a9:96a4:2939:bac2:87e7:251b:d58d, 204.209.198.79, 81.245.129.177, 74.255.240.36, 50.188.246.246, a35:86c4:162e:4a1b:202b:dc58:82a:1cca, 5ee4:e6a4:6d8e:af46:a1c8:889c:4f05:958a, babe:ab13:9ec6:b88d:5b6a:5729:1570:576f, and 103.52.15.204, as of 5:34:16 AM on 3-19-24?

#!/usr/bin/env python

import pybgpstream
from itertools import groupby

# Target time (UTC)
FROM_TIME = "2024-03-19 05:34:16"
UNTIL_TIME = "2024-03-19 05:34:16"

# VPs to combine (peer IP addresses)
VP_IPS = {
    "143.192.143.111",
    "238:81a9:96a4:2939:bac2:87e7:251b:d58d",
    "204.209.198.79",
    "81.245.129.177",
    "74.255.240.36",
    "50.188.246.246",
    "a35:86c4:162e:4a1b:202b:dc58:82a:1cca",
    "5ee4:e6a4:6d8e:af46:a1c8:889c:4f05:958a",
    "babe:ab13:9ec6:b88d:5b6a:5729:1570:576f",
    "103.52.15.204",
}

# Build a RIB stream around the specified time (all collectors, v4+v6)
stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="ribs",
)

total_len = 0
path_count = 0

for rec in stream.records():
    for elem in rec:
        # Keep only elements from the selected VPs
        if elem.peer_address not in VP_IPS:
            continue

        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        # Remove repeatedly prepended ASNs (path compression)
        hops = [k for k, _ in groupby(aspath.split())]
        if len(hops) == 0:
            continue

        total_len += len(hops)
        path_count += 1

if path_count == 0:
    print("No matching paths found for the given VPs and time.")
else:
    avg_len = float(total_len) / path_count
    print("Average AS path length:", avg_len)
