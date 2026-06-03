# How many autonomous systems are on the Internet routing in IPv6?

import pybgpstream

# Time interval to analyze (UTC). Adjust as needed.
FROM_TIME = "2025-01-01 00:00:00"
UNTIL_TIME = "2025-01-01 23:59:59"

# Build a stream of IPv6 RIBs over the chosen interval
stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="ribs",
    filter="ipversion 6"
)

ipv6_asns = set()

for rec in stream.records():
    for elem in rec:
        # Peer AS
        ipv6_asns.add(str(elem.peer_asn))
        # ASes in the AS path (including origin)

        aspath = elem.fields.get("as-path")
        if aspath:
            for asn in aspath.split():
                ipv6_asns.add(asn)

print(len(ipv6_asns))
