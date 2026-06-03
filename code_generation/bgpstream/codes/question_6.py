# Are AS397142 and AS19647 directly connected?

import pybgpstream
from itertools import groupby

AS_A = "397142"
AS_B = "19647"

# Time window to inspect (UTC) – adjust as needed
FROM_TIME = "2024-03-01 00:00:00"
UNTIL_TIME = "2024-03-01 23:59:59"

# RIB snapshot, all collectors
stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="ribs",
    # Pre-filter for paths where the two ASes are adjacent in either order
    filter=f"aspath _{AS_A}_{AS_B}_|_{AS_B}_{AS_A}_"
)

direct = False
examples = set()

for rec in stream.records():
    for elem in rec:
        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        # Remove repeatedly prepended ASNs
        hops = [k for k, _ in groupby(aspath.split())]
        if len(hops) < 2:
            continue

        for u, v in zip(hops, hops[1:]):
            if (u == AS_A and v == AS_B) or (u == AS_B and v == AS_A):
                direct = True
                examples.add(aspath)
                break
        if direct:
            # Comment this break out if you want to scan full dataset
            break
    if direct:
        break

if direct:
    print(f"Yes, AS{AS_A} and AS{AS_B} appear directly connected.")
    print("Example AS path(s):")
    for p in examples:
        print(p)
else:
    print(f"No, AS{AS_A} and AS{AS_B} do not appear directly connected in this dataset.")
