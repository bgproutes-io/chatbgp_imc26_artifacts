# Give me all the AS paths containing AS number 136557 during the time frame of March 5, 2024 at 12:48:54 AM to March 25, 2024 at 4:59:40 AM. Only consider the VP 143.192.143.111.

import pybgpstream

TARGET_ASN = "136557"
VP_IP = "143.192.143.111"

FROM_TIME = "2024-03-05 00:48:54"
UNTIL_TIME = "2024-03-25 04:59:40"

# Build the stream: updates only, pre-filter on AS path containing 136557
stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="updates",
    filter=f"aspath _{TARGET_ASN}_"
)

paths = set()

for rec in stream.records():
    for elem in rec:
        # Only consider the specified VP
        if elem.peer_address != VP_IP:
            continue

        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        # By construction, all aspaths already contain TARGET_ASN,
        # just collect them (deduplicated)
        paths.add(aspath)

# Print all unique AS paths containing 136557 seen from this VP & time range
for p in sorted(paths):
    print(p)


