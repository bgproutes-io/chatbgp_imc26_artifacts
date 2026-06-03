# Which autonomous systems (ASes) always appear at the start or end of the AS paths (never in the middle), and have a minimum of two distinct neighbors? Consider only IPv6 peers.

import pybgpstream
from collections import defaultdict
from itertools import groupby

# Only IPv6 prefixes (thus IPv6 peers)
stream = pybgpstream.BGPStream(
    record_type="ribs",
    filter="ipversion 6"
)

appears_first = defaultdict(bool)
appears_last = defaultdict(bool)
appears_middle = defaultdict(bool)
neighbors = defaultdict(set)

for rec in stream.records():
    for elem in rec:
        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        # Remove repeatedly prepended ASNs
        hops = [k for k, _ in groupby(aspath.split())]
        if not hops:
            continue

        n = len(hops)
        for i, asn in enumerate(hops):
            # Track position of this ASN in the path
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

            # Track neighbors (adjacent ASNs in the path)
            if i > 0:
                neighbors[asn].add(hops[i - 1])
            if i < n - 1:
                neighbors[asn].add(hops[i + 1])

# Select ASes that never appear in the middle, but appear at start and/or end,
# and have at least two distinct neighbors
result = []
for asn in neighbors.keys():
    if appears_middle[asn]:
        continue
    if not (appears_first[asn] or appears_last[asn]):
        continue
    if len(neighbors[asn]) < 2:
        continue
    result.append((asn, sorted(neighbors[asn])))

# Print results
for asn, neighs in sorted(result, key=lambda x: int(x[0])):
    print("AS{} neighbors: {}".format(asn, ",".join(neighs)))
