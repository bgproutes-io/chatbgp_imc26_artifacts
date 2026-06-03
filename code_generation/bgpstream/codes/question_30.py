# How many distinct \24 prefixes does AS11543 announce in IPv6 at 11:07:25 PM on 3/13/2024?

#!/usr/bin/env python

import pybgpstream
import ipaddress

TARGET_AS = "11543"
TIME_FROM = "2024-03-13 23:07:25"
TIME_UNTIL = "2024-03-13 23:07:25"

stream = pybgpstream.BGPStream(
    from_time=TIME_FROM,
    until_time=TIME_UNTIL,
    record_type="ribs",
    filter="ipversion 4",
)

prefixes_24 = set()

for rec in stream.records():
    for elem in rec:
        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        ases = aspath.split()
        if not ases or ases[-1] != TARGET_AS:
            continue

        pfx = elem.fields.get("prefix")
        if not pfx:
            continue

        try:
            net = ipaddress.ip_network(pfx, strict=False)
        except ValueError:
            continue

        if net.version == 4 and net.prefixlen == 24:
            prefixes_24.add(str(net))

print("Number of distinct /24 prefixes announced by AS{}: {}".format(
    TARGET_AS, len(prefixes_24)
))
