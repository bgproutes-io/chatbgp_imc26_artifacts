# Which updates within the timeframe of 8:10 p.m. to 8:50 p.m. on March 30, 2024 include one or more large community?

#!/usr/bin/env python

import pybgpstream

FROM_TIME = "2024-03-30 20:10:00"
UNTIL_TIME = "2024-03-30 20:50:00"

# All collectors, updates only, specified time window
stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="updates",
)

for rec in stream.records():
    for elem in rec:
        # Only announcements/withdrawals are "updates" at elem level
        if elem.type not in ("A", "W"):
            continue

        # Large communities are typically exposed as "large-communities"
        large_comms = elem.fields.get("large-communities")
        if not large_comms:
            continue

        print(
            "time={} project={} collector={} peer={} peer_asn={} prefix={} large_communities={}".format(
                rec.time,
                rec.project,
                rec.collector,
                elem.peer_address,
                elem.peer_asn,
                elem.fields.get("prefix"),
                ",".join(sorted(large_comms)),
            )
        )
