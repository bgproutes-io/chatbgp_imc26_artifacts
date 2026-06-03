# Can you identify the ASes that utilized AS path prepending (i.e., which prepends consecutively its AS number multiple times in the AS path) on March 19, 2024 at 5:34:16 AM?

import pybgpstream

FROM_TIME = "2024-03-19 05:34:16"
UNTIL_TIME = "2024-03-19 05:34:16"

stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="ribs",
)

prepending_ases = set()

for rec in stream.records():
    for elem in rec:
        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        hops = aspath.split()
        if len(hops) < 2:
            continue

        # Detect consecutive duplicates (prepending)
        last = hops[0]
        for asn in hops[1:]:
            if asn == last:
                prepending_ases.add(asn)
            last = asn

for asn in sorted(prepending_ases, key=int):
    print(asn)
