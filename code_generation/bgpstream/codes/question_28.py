# Return the AS paths where AS 11543 is the last AS. Use collectors babe:ab13:9ec6:b88d:5b6a:5729:1570:576f, a35:86c4:162e:4a1b:202b:dc58:82a:1cca, 74.255.240.36, 204.209.198.79, 103.52.15.204, 143.192.143.111, 50.188.246.246, and 238:81a9:96a4:2939:bac2:87e7:251b:d58d, and consider the updates between 02:17:10 on March 25, 2024 and 19:05:12 on March 27, 2024?

#!/usr/bin/env python

import pybgpstream

TARGET_AS = "11543"

FROM_TIME = "2024-03-25 02:17:10"
UNTIL_TIME = "2024-03-27 19:05:12"

VP_IPS = {
    "babe:ab13:9ec6:b88d:5b6a:5729:1570:576f",
    "a35:86c4:162e:4a1b:202b:dc58:82a:1cca",
    "74.255.240.36",
    "204.209.198.79",
    "103.52.15.204",
    "143.192.143.111",
    "50.188.246.246",
    "238:81a9:96a4:2939:bac2:87e7:251b:d58d",
}

stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="updates",
    filter=f"aspath _{TARGET_AS}_",
)

paths = set()

for rec in stream.records():
    for elem in rec:
        if elem.peer_address not in VP_IPS:
            continue
        if elem.type not in ("A", "W"):
            continue

        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        ases = aspath.split()
        if not ases:
            continue

        if ases[-1] == TARGET_AS:
            paths.add(aspath)

for p in sorted(paths):
    print(p)
