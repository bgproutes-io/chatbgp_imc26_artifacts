# What is the most recent day where AS1951 and AS2876 appear disconnected (i.e., not seen directly connected in any AS path) from all vantage points and in both IPv4 and IPv6?

#!/usr/bin/env python

import pybgpstream
from itertools import groupby
from datetime import datetime, timedelta

AS_A = "1951"
AS_B = "2876"

# Scan backward day by day until a day is found where the two ASes
# are NOT directly adjacent in ANY AS path in BOTH IPv4 and IPv6.
# Adjust the search horizon as needed.
END_DAY = datetime.utcnow().date()
START_DAY = END_DAY - timedelta(days=365)

def day_has_direct_connection(day):
    day_from = f"{day} 00:00:00"
    day_until = f"{day} 23:59:59"

    for ipver in (4, 6):
        stream = pybgpstream.BGPStream(
            from_time=day_from,
            until_time=day_until,
            record_type="ribs",
            filter=f"ipversion {ipver} and (aspath _{AS_A}_{AS_B}_|_{AS_B}_{AS_A}_)"
        )

        for rec in stream.records():
            for elem in rec:
                aspath = elem.fields.get("as-path")
                if not aspath:
                    continue

                hops = [k for k, _ in groupby(aspath.split())]
                if len(hops) < 2:
                    continue

                for u, v in zip(hops, hops[1:]):
                    if (u == AS_A and v == AS_B) or (u == AS_B and v == AS_A):
                        return True  # adjacency exists this day

    return False  # no adjacency found in either IPv4 or IPv6


most_recent_disconnected = None

d = END_DAY
while d >= START_DAY:
    if not day_has_direct_connection(d):
        most_recent_disconnected = d
        break
    d -= timedelta(days=1)

if most_recent_disconnected:
    print("Most recent day with NO AS1951–AS2876 adjacency:", most_recent_disconnected)
else:
    print("No day without adjacency found in the scanned interval.")
