# For every VP, return the increase in the number of distinct AS links observed between the dates 9 March 2024 and 21 March 2024?

import pybgpstream
from itertools import groupby
from collections import defaultdict

# Days to compare (UTC)
DAY1_FROM = "2024-03-09 00:00:00"
DAY1_UNTIL = "2024-03-09 23:59:59"

DAY2_FROM = "2024-03-21 00:00:00"
DAY2_UNTIL = "2024-03-21 23:59:59"


def collect_links(from_time, until_time):
    """
    Return a dict:
        peer_address -> set of undirected AS links (tuples (a,b) with a<b)
    observed in RIBs during [from_time, until_time].
    """
    stream = pybgpstream.BGPStream(
        from_time=from_time,
        until_time=until_time,
        record_type="ribs",
    )

    vp_links = defaultdict(set)

    for rec in stream.records():
        for elem in rec:
            aspath = elem.fields.get("as-path")
            if not aspath:
                continue

            hops = [k for k, _ in groupby(aspath.split())]
            if len(hops) < 2:
                continue

            peer = elem.peer_address
            if peer is None:
                continue

            for u, v in zip(hops, hops[1:]):
                if u == v:
                    continue
                a, b = sorted((u, v), key=int)
                vp_links[peer].add((a, b))

    return vp_links


links_day1 = collect_links(DAY1_FROM, DAY1_UNTIL)
links_day2 = collect_links(DAY2_FROM, DAY2_UNTIL)

all_vps = set(links_day1.keys()) | set(links_day2.keys())

for vp in sorted(all_vps):
    l1 = links_day1.get(vp, set())
    l2 = links_day2.get(vp, set())
    increase = len(l2) - len(l1)
    print(
        "VP {}: distinct links on 2024-03-09 = {}, on 2024-03-21 = {}, increase = {}".format(
            vp, len(l1), len(l2), increase
        )
    )
