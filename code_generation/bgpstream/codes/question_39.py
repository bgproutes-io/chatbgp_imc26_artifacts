# What community values are included in BGP updates for prefix 8.12.55.0/24 on March 6, 2024, at 7:09 PM? Use VPs 5ee4:e6a4:6d8e:af46:a1c8:889c:4f05:958a, 74.255.240.36, 238:81a9:96a4:2939:bac2:87e7:251b:d58d, 204.209.198.79, and 103.52.15.204.

import pybgpstream

PREFIX = "8.12.55.0/24"

FROM_TIME = "2024-03-06 19:09:00"
UNTIL_TIME = "2024-03-06 19:09:59"

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
    record_type="updates",
    filter=f"prefix exact {PREFIX}"
)

all_communities = set()

for rec in stream.records():
    for elem in rec:
        # Only use specified VPs
        if elem.peer_address not in VP_IPS:
            continue

        # Only announcements/withdrawals
        if elem.type not in ("A", "W"):
            continue

        comms = elem.fields.get("communities")
        if not comms:
            continue

        for c in comms:
            all_communities.add(c)

for c in sorted(all_communities):
    print(c)