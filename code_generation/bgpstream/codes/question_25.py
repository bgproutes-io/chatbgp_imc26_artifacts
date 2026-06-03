# Is the IPv6 subnet A563:febc:5479:9c09:1146:89c0:796b:20c1/52 in a RIB?

#!/usr/bin/env python

import pybgpstream

PREFIX = "A563:febc:5479:9c09:1146:89c0:796b:20c1/52"

# Search RIBs for this exact IPv6 prefix (all collectors, full history as allowed)
stream = pybgpstream.BGPStream(
    record_type="ribs",
    filter=f"ipversion 6 and prefix exact {PREFIX}"
)

found = False

for rec in stream.records():
    for elem in rec:
        pfx = elem.fields.get("prefix")
        if pfx == PREFIX:
            found = True
            print(
                "Found in RIB: time={} project={} collector={} peer={} peer_asn={} prefix={} aspath={}".format(
                    rec.time,
                    rec.project,
                    rec.collector,
                    elem.peer_address,
                    elem.peer_asn,
                    pfx,
                    elem.fields.get("as-path"),
                )
            )

if not found:
    print(f"Prefix {PREFIX} not found in any RIB examined.")
