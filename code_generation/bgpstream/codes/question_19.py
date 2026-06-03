# Which BGP updates include the two (both of them) community attributes 656:200 and 3456:45673 between March 23, 2024 at 4:31 AM and March 31, 2024 at 6:56 AM?

import pybgpstream

FROM_TIME = "2024-03-23 04:31:00"
UNTIL_TIME = "2024-03-31 06:56:00"

REQUIRED_COMMS = {"656:200", "3456:45673"}

stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="updates",
)

for rec in stream.records():
    for elem in rec:
        # Only announcements / withdrawals
        if elem.type not in ("A", "W"):
            continue

        comms = elem.fields.get("communities")
        if not comms:
            continue

        print (comms)
        # Communities is a set of strings in "asn:value" format
        if not REQUIRED_COMMS.issubset(comms):
            continue

        print(
            "time={} project={} collector={} peer={} peer_asn={} type={} "
            "prefix={} nexthop={} aspath={} communities={}".format(
                rec.time,
                rec.project,
                rec.collector,
                elem.peer_address,
                elem.peer_asn,
                elem.type,
                elem.fields.get("prefix"),
                elem.fields.get("next-hop"),
                elem.fields.get("as-path"),
                ",".join(sorted(comms)),
            )
        )