# How many distinct community values are associated with AS number 2977 (i.e., that begin with 2977). Consider the VPs 143.192.143.111, 50.188.246.246, 103.52.15.204, and 238:81a9:96a4:2939:bac2:87e7:251b:d58d?

#!/usr/bin/env python

import pybgpstream

TARGET_AS = "2977"

VPS = {
    "143.192.143.111",
    "50.188.246.246",
    "103.52.15.204",
    "238:81a9:96a4:2939:bac2:87e7:251b:d58d",
}

# RIBs only, all time, restrict to paths containing AS2977 to limit scan
stream = pybgpstream.BGPStream(
    record_type="ribs",
    filter=f"aspath _{TARGET_AS}_"
)

communities_2977 = set()

for rec in stream.records():
    for elem in rec:
        if elem.peer_address not in VPS:
            continue

        comms = elem.fields.get("communities")
        if not comms:
            continue

        for c in comms:
            if c.startswith(f"{TARGET_AS}:"):
                communities_2977.add(c)

print("Number of distinct communities with ASN 2977:", len(communities_2977))
for c in sorted(communities_2977):
    print(c)
