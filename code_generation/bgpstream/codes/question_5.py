# What is the minimum number of AS hops between Autonomous System 140627 and Autonomous System 45204, based on the data collected from the following VPs: 143.192.143.111, 238:81a9:96a4:2939:bac2:87e7:251b:d58d, 204.209.198.79, 81.245.129.177, 74.255.240.36, 50.188.246.246, a35:86c4:162e:4a1b:202b:dc58:82a:1cca, 5ee4:e6a4:6d8e:af46:a1c8:889c:4f05:958a, babe:ab13:9ec6:b88d:5b6a:5729:1570:576f, and 103.52.15.204 at 11:29:11 AM on March Seventh, 2024.

import pybgpstream
import networkx as nx
from itertools import groupby

TARGET_SRC = "140627"
TARGET_DST = "45204"

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

FROM_TIME = "2024-03-07 11:29:11"
UNTIL_TIME = "2024-03-07 11:29:11"

stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="ribs",
)

G = nx.Graph()

for rec in stream.records():
    for elem in rec:
        # Only consider paths from the specified VPs
        if elem.peer_address not in VP_IPS:
            continue

        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        # Remove repeatedly prepended ASNs
        hops = [k for k, _ in groupby(aspath.split())]
        if len(hops) < 2:
            continue

        # Add edges for each adjacency in the AS path
        for u, v in zip(hops, hops[1:]):
            G.add_edge(u, v)

# Compute the minimum number of AS hops between TARGET_SRC and TARGET_DST
if G.has_node(TARGET_SRC) and G.has_node(TARGET_DST) and nx.has_path(G, TARGET_SRC, TARGET_DST):
    path = nx.shortest_path(G, TARGET_SRC, TARGET_DST)
    min_hops = len(path) - 1
    print("Minimum number of AS hops between {} and {}: {}".format(
        TARGET_SRC, TARGET_DST, min_hops
    ))
    print("Path:", " ".join(path))
else:
    print("No path found between {} and {} in the collected data.".format(
        TARGET_SRC, TARGET_DST
    ))






