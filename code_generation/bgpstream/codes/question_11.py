# When AS48219 and AS64327 started to be directly connected for the first time in IPv6. Consider data from peers 143.192.143.111, 238:81a9:96a4:2939:bac2:87e7:251b:d58d, 204.209.198.79, 81.245.129.177, 74.255.240.36, 50.188.246.246, a35:86c4:162e:4a1b:202b:dc58:82a:1cca, 5ee4:e6a4:6d8e:af46:a1c8:889c:4f05:958a, babe:ab13:9ec6:b88d:5b6a:5729:1570:576f, and 103.52.15.204?

#!/usr/bin/env python

import pybgpstream
from itertools import groupby

AS_A = "48219"
AS_B = "64327"

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

# IPv6 only, no time restriction — scan entire archive chronologically
stream = pybgpstream.BGPStream(
    record_type="ribs",
    filter="ipversion 6"
)

first_time = None
first_path = None
first_peer = None

for rec in stream.records():
    for elem in rec:
        if elem.peer_address not in IPV6_VPS:
            continue

        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        # Remove AS prepends
        hops = [k for k, _ in groupby(aspath.split())]
        if len(hops) < 2:
            continue

        # Detect adjacency
        for u, v in zip(hops, hops[1:]):
            if (u == AS_A and v == AS_B) or (u == AS_B and v == AS_A):
                first_time = rec.time
                first_path = aspath
                first_peer = elem.peer_address
                break

        if first_time is not None:
            break
    if first_time is not None:
        break

if first_time is None:
    print(f"AS{AS_A} and AS{AS_B} never appear directly connected in IPv6.")
else:
    print("First IPv6 direct adjacency observed:")
    print("Time:", first_time)
    print("Peer:", first_peer)
    print("AS Path:", first_path)
