# What is the total number of distinct prefixes that can be observed in both IPv4 and IPv6?

import pybgpstream

FROM_TIME = "2024-03-01 00:00:00"
UNTIL_TIME = "2024-03-01 23:59:59"

# IPv4 prefixes
stream_v4 = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="ribs",
    filter="ipversion 4"
)

# IPv6 prefixes
stream_v6 = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="ribs",
    filter="ipversion 6"
)

prefixes_v4 = set()
prefixes_v6 = set()

for rec in stream_v4.records():
    for elem in rec:
        pfx = elem.fields.get("prefix")
        if pfx:
            prefixes_v4.add(pfx)

for rec in stream_v6.records():
    for elem in rec:
        pfx = elem.fields.get("prefix")
        if pfx:
            prefixes_v6.add(pfx)

all_prefixes = prefixes_v4 | prefixes_v6

print("Distinct IPv4 prefixes:", len(prefixes_v4))
print("Distinct IPv6 prefixes:", len(prefixes_v6))
print("Total distinct prefixes (IPv4 + IPv6):", len(all_prefixes))