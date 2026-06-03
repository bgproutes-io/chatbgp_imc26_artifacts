# Return the ASes that are directly connected to Autonomous System 174 in the AS paths but also that never appear at the beginning or at the end of any AS path. Consider the data from VPs 143.192.143.111, 50.188.246.246, 103.52.15.204, and 238:81a9:96a4:2939:bac2:87e7:251b:d58d?

#!/usr/bin/env python

import pybgpstream
from itertools import groupby
from collections import defaultdict

TARGET_AS = "174"

# VPs to consider (peer IP addresses)
VP_IPS = {
    "143.192.143.111",
    "50.188.246.246",
    "103.52.15.204",
    "238:81a9:96a4:2939:bac2:87e7:251b:d58d",
}

# Use RIBs from all collectors (time window can be added if desired)
stream = pybgpstream.BGPStream(
    record_type="ribs",
)

neighbors_of_174 = set()
appears_first = defaultdict(bool)
appears_last = defaultdict(bool)

for rec in stream.records():
    for elem in rec:
        # Only consider elems coming from the specified VPs
        if elem.peer_address not in VP_IPS:
            continue

        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        # Remove repeatedly prepended ASNs
        hops = [k for k, _ in groupby(aspath.split())]
        if len(hops) == 0:
            continue

        # Track where each AS appears (start/end)
        appears_first[hops[0]] = True
        appears_last[hops[-1]] = True

        # Track ASes directly connected to AS174
        for u, v in zip(hops, hops[1:]):
            if u == TARGET_AS:
                neighbors_of_174.add(v)
            elif v == TARGET_AS:
                neighbors_of_174.add(u)

# Keep only neighbors that never appear at the beginning or end of any AS path
result = sorted(
    asn for asn in neighbors_of_174
    if not appears_first[asn] and not appears_last[asn]
)

for asn in result:
    print(asn)
