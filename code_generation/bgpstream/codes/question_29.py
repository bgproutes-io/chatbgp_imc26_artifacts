# What percentage of ASes announcing an IPv4 prefix also announce an IPv6 prefix on 03.01.24 at 0700 hours?

#!/usr/bin/env python

import pybgpstream

TIME_FROM = "2024-03-01 07:00:00"
TIME_UNTIL = "2024-03-01 07:00:00"

def get_origin_ases(ipver):
    stream = pybgpstream.BGPStream(
        from_time=TIME_FROM,
        until_time=TIME_UNTIL,
        record_type="ribs",
        filter=f"ipversion {ipver}",
    )

    origins = set()

    for rec in stream.records():
        for elem in rec:
            aspath = elem.fields.get("as-path")
            if not aspath:
                continue

            ases = aspath.split()
            if ases:
                origins.add(ases[-1])

    return origins


v4_origins = get_origin_ases(4)
v6_origins = get_origin_ases(6)

if not v4_origins:
    print("No IPv4-origin ASes observed.")
else:
    pct = 100 * len(v4_origins & v6_origins) / len(v4_origins)
    print("Number of ASes announcing IPv4 prefixes:", len(v4_origins))
    print("Number of ASes announcing IPv6 prefixes:", len(v6_origins))
    print("Number announcing both:", len(v4_origins & v6_origins))
    print("Percentage:", pct)
