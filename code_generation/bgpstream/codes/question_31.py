# Could you tell me the size of the RIB of each of the following VPs: 143.192.143.111, 50.188.246.246, 103.52.15.204, and 238:81a9:96a4:2939:bac2:87e7:251b:d58d?

#!/usr/bin/env python

import pybgpstream
from collections import defaultdict

VPS = {
    "143.192.143.111",
    "50.188.246.246",
    "103.52.15.204",
    "238:81a9:96a4:2939:bac2:87e7:251b:d58d",
}

# Reference time window for RIB snapshot (adjust if needed)
FROM_TIME = "2024-03-01 00:00:00"
UNTIL_TIME = "2024-03-01 00:00:00"

stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="ribs",
)

# For each VP, store distinct (prefix, as-path) tuples
vp_rib_entries = defaultdict(set)

for rec in stream.records():
    for elem in rec:
        vp = elem.peer_address
        if vp not in VPS:
            continue

        pfx = elem.fields.get("prefix")
        aspath = elem.fields.get("as-path")
        if not pfx or not aspath:
            continue

        vp_rib_entries[vp].add((pfx, aspath))

for vp in sorted(VPS):
    size = len(vp_rib_entries.get(vp, set()))
    print(f"VP {vp}: RIB size (distinct prefix + AS path entries) = {size}")
