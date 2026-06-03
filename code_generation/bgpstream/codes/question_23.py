# Which updates were observed for Prefix 235.38.113.145/22 by peers 143.192.143.111, 238:81a9:96a4:2939:bac2:87e7:251b:d58d, 204.209.198.79, 81.245.129.177, 74.255.240.36, 50.188.246.246, a35:86c4:162e:4a1b:202b:dc58:82a:1cca, 5ee4:e6a4:6d8e:af46:a1c8:889c:4f05:958a, babe:ab13:9ec6:b88d:5b6a:5729:1570:576f and 103.52.15.204 between 06:49:16 on March 26, 2024, and 18:10:52 on March 30, 2024?

import pybgpstream

FROM_TIME = "2024-03-26 06:49:16"
UNTIL_TIME = "2024-03-30 18:10:52"
PREFIX = "235.38.113.145/22"

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

stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="updates",
    filter=f"prefix exact {PREFIX}"
)

for rec in stream.records():
    for elem in rec:
        if elem.peer_address not in VP_IPS:
            continue
        if elem.type not in ("A", "W"):
            continue
        print(
            "time={} project={} collector={} peer={} peer_asn={} type={} prefix={} nexthop={} aspath={}".format(
                rec.time,
                rec.project,
                rec.collector,
                elem.peer_address,
                elem.peer_asn,
                elem.type,
                elem.fields.get("prefix"),
                elem.fields.get("next-hop"),
                elem.fields.get("as-path"),
            )
        )