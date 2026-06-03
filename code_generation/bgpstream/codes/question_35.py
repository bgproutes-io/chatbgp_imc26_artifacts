# How often does the path from AS 56445 to AS 41030 (or the sub path, if AS 56448 or AS41030 are not at one end of the path) corresponds to the reversed path (or sub path) from AS 41030 to AS 56445 on March 30th, 2024 at 08:00 hours using IPv6? Consider the VPs VPs 5ee4:e6a4:6d8e:af46:a1c8:889c:4f05:958a, 74.255.240.36, 238:81a9:96a4:2939:bac2:87e7:251b:d58d, 204.209.198.79, and 103.52.15.204.

#!/usr/bin/env python

import pybgpstream
from collections import Counter

AS_A = "56445"
AS_B = "41030"

FROM_TIME = "2024-03-30 08:00:00"
UNTIL_TIME = "2024-03-30 08:00:00"

VP_IPS = {
    "5ee4:e6a4:6d8e:af46:a1c8:889c:4f05:958a",
    "74.255.240.36",
    "238:81a9:96a4:2939:bac2:87e7:251b:d58d",
    "204.209.198.79",
    "103.52.15.204",
}

stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="ribs",
    filter=f"ipversion 6 and aspath _{AS_A}_{AS_B}_|_{AS_B}_{AS_A}_"
)

subpaths_fwd = Counter()  # AS_A -> AS_B
subpaths_rev = Counter()  # AS_B -> AS_A
total_fwd = 0
total_rev = 0

for rec in stream.records():
    for elem in rec:
        if elem.peer_address not in VP_IPS:
            continue

        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        hops = aspath.split()
        if len(hops) < 2:
            continue

        positions_a = [i for i, a in enumerate(hops) if a == AS_A]
        positions_b = [i for i, a in enumerate(hops) if a == AS_B]

        if not positions_a or not positions_b:
            continue

        for i in positions_a:
            for j in positions_b:
                if i < j:
                    sp = tuple(hops[i:j + 1])
                    subpaths_fwd[sp] += 1
                    total_fwd += 1
                elif j < i:
                    sp = tuple(hops[j:i + 1])
                    subpaths_rev[sp] += 1
                    total_rev += 1

matches = 0
for sp, c in subpaths_fwd.items():
    rev_sp = tuple(reversed(sp))
    if rev_sp in subpaths_rev:
        matches += min(c, subpaths_rev[rev_sp])

print("Total AS paths/subpaths {} -> {}: {}".format(AS_A, AS_B, total_fwd))
print("Total AS paths/subpaths {} -> {}: {}".format(AS_B, AS_A, total_rev))
print("Number of times the path/subpath matches the reversed one:", matches)

print("\nMatching subpaths (A->B) and their counts:")
for sp, c in sorted(subpaths_fwd.items(), key=lambda x: x[0]):
    rev_sp = tuple(reversed(sp))
    if rev_sp in subpaths_rev:
        print("A->B: {}  count_AtoB={}  count_BtoA={}".format(
            " ".join(sp), c, subpaths_rev[rev_sp]
        ))
