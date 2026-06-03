# How many Autonomous Systems are always found in the middle of the AS paths and never at the endpoints, consider only IPv4 and peers babe:ab13:9ec6:b88d:5b6a:5729:1570:576f, a35:86c4:162e:4a1b:202b:dc58:82a:1cca, 74.255.240.36, 204.209.198.79, 103.52.15.204, 143.192.143.111, 50.188.246.246, and 238:81a9:96a4:2939:bac2:87e7:251b:d58d?

#!/usr/bin/env python

import pybgpstream
from collections import defaultdict
from itertools import groupby

# Time window (UTC) – adjust if needed
FROM_TIME = "2024-03-22 00:00:00"
UNTIL_TIME = "2024-03-22 23:59:59"

IPV4_VPS = {
    "babe:ab13:9ec6:b88d:5b6a:5729:1570:576f",
    "a35:86c4:162e:4a1b:202b:dc58:82a:1cca",
    "74.255.240.36",
    "204.209.198.79",
    "103.52.15.204",
    "143.192.143.111",
    "50.188.246.246",
    "238:81a9:96a4:2939:bac2:87e7:251b:d58d",
}

stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="ribs",
    filter="ipversion 4",
)

appears_first = defaultdict(bool)
appears_last = defaultdict(bool)
appears_middle = defaultdict(bool)

for rec in stream.records():
    for elem in rec:
        if elem.peer_address not in IPV4_VPS:
            continue

        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        # Remove AS prepends so middle positions are meaningful
        hops = [k for k, _ in groupby(aspath.split())]
        if not hops:
            continue

        n = len(hops)
        for i, asn in enumerate(hops):
            if n == 1:
                appears_first[asn] = True
                appears_last[asn] = True
            else:
                if i == 0:
                    appears_first[asn] = True
                elif i == n - 1:
                    appears_last[asn] = True
                else:
                    appears_middle[asn] = True

# ASes that always appear only in the middle (never at endpoints)
result = [
    asn
    for asn in set(
        list(appears_first.keys())
        + list(appears_last.keys())
        + list(appears_middle.keys())
    )
    if appears_middle[asn] and not appears_first[asn] and not appears_last[asn]
]

print("Number of ASes that always appear only in the middle of AS paths:", len(result))
print("ASNs:", " ".join(sorted(result, key=int)))
