# What was the first time that AS11543 appear in the routing table?

import pybgpstream

TARGET_AS = "11543"

# No time filter → bgpstream scans from earliest available data
stream = pybgpstream.BGPStream(
    record_type="ribs",
    filter=f"aspath _{TARGET_AS}_"
)

first_time = None

for rec in stream.records():
    for elem in rec:
        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        ases = aspath.split()
        if TARGET_AS not in ases:
            continue

        t = rec.time
        if first_time is None or t < first_time:
            first_time = t

if first_time is None:
    print(f"AS{TARGET_AS} never appears in any RIB in the dataset.")
else:
    print(f"First observed time of AS{TARGET_AS}: {first_time}")