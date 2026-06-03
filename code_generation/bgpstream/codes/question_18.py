# Which updates include blackholing communities during the timeframe of 05:34 AM on March 12, 2024 to 03:59 AM on March 13, 2024?

#!/usr/bin/env python

import pybgpstream

FROM_TIME = "2024-03-12 05:34:00"
UNTIL_TIME = "2024-03-13 03:59:00"

# Common blackholing community values (extend as needed)
BLACKHOLE_VALUES = {
    "666",
    "777",
    "999",
    "6666",
    "6667",
}

def is_blackhole_community(c):
    """
    c is in 'asn:value' format.
    Return True if the value part is one of the known blackhole values.
    """
    parts = c.split(":")
    if len(parts) != 2:
        return False
    _, val = parts
    return val in BLACKHOLE_VALUES

stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="updates",
)

for rec in stream.records():
    for elem in rec:
        # Only BGP updates (announcements and withdrawals)
        if elem.type not in ("A", "W"):
            continue

        comms = elem.fields.get("communities")
        if not comms:
            continue

        bh_comms = [c for c in comms if is_blackhole_community(c)]
        if not bh_comms:
            continue

        print(
            "time={} project={} collector={} peer={} peer_asn={} type={} prefix={} nexthop={} aspath={} blackhole_communities={}".format(
                rec.time,
                rec.project,
                rec.collector,
                elem.peer_address,
                elem.peer_asn,
                elem.type,
                elem.fields.get("prefix"),
                elem.fields.get("next-hop"),
                elem.fields.get("as-path"),
                ",".join(sorted(bh_comms)),
            )
        )
