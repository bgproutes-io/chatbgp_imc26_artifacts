# From the IPv6 peers 143.192.143.111, 238:81a9:96a4:2939:bac2:87e7:251b:d58d, 204.209.198.79, 81.245.129.177, 74.255.240.36, 50.188.246.246, a35:86c4:162e:4a1b:202b:dc58:82a:1cca, 5ee4:e6a4:6d8e:af46:a1c8:889c:4f05:958a, babe:ab13:9ec6:b88d:5b6a:5729:1570:576f, and 103.52.15.204 on 03-22-24, how many ASes appears always at the ends of the AS path and never appear in the middle?

#!/usr/bin/env python

import pybgpstream
from collections import defaultdict
from itertools import groupby

FROM_TIME = "2024-03-22 00:00:00"
UNTIL_TIME = "2024-03-22 23:59:59"

IPV6_VPS = {
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

stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="ribs",
    filter="ipversion 6",
)

appears_first = defaultdict(bool)
appears_last = defaultdict(bool)
appears_middle = defaultdict(bool)

for rec in stream.records():
    for elem in rec:
        if elem.peer_address not in IPV6_VPS:
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

# ASes that appear only at the ends (never in the middle)
result = [
    asn for asn in set(list(appears_first.keys()) + list(appears_last.keys()))
    if (appears_first[asn] or appears_last[asn]) and not appears_middle[asn]
]

print("Number of ASes that only appear at the ends of AS paths (never in the middle):", len(result))
print("ASNs:", " ".join(sorted(result, key=int)))
