# What are the Autonomous Systems that originate the prefix 133.7.254.105/23 (i.e., are at the end of the AS path) as seen from BGP routers?

import pybgpstream

PREFIX = "133.7.254.105/23"

stream = pybgpstream.BGPStream(
    record_type="ribs",
    filter=f"ipversion 4 and prefix exact {PREFIX}",
)

origins = set()

for rec in stream.records():
    for elem in rec:
        pfx = elem.fields.get("prefix")
        if pfx != PREFIX:
            continue

        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        ases = aspath.split()
        if ases:
            origins.add(ases[-1])

for origin in sorted(origins, key=int):
    print(origin)