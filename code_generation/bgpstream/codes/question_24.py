# Does AS 48152 appear in an AS path used to reach the prefix 34.131.22.129/18. Consider collectors babe:ab13:9ec6:b88d:5b6a:5729:1570:576f, a35:86c4:162e:4a1b:202b:dc58:82a:1cca, 74.255.240.36, 204.209.198.79, 103.52.15.204, 143.192.143.111, 50.188.246.246, and 238:81a9:96a4:2939:bac2:87e7:251b:d58d on March 1, 2024, at 3:21:05 PM?

import pybgpstream

TARGET_AS = "48152"
PREFIX = "34.131.22.129/18"

FROM_TIME = "2024-03-01 15:21:05"
UNTIL_TIME = "2024-03-01 15:21:05"

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
    record_type="ribs",
    filter=f"prefix exact {PREFIX}"
)

found = False
paths = set()

for rec in stream.records():
    for elem in rec:
        if elem.peer_address not in VP_IPS:
            continue

        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        if TARGET_AS in aspath.split():
            found = True
            paths.add(aspath)

if found:
    print(f"Yes, AS{TARGET_AS} appears in AS paths to {PREFIX}. Example path(s):")
    for p in sorted(paths):
        print(p)
else:
    print(f"No, AS{TARGET_AS} does not appear in any AS path to {PREFIX} from the given VPs at that time.")
