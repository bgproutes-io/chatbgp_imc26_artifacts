# Which prefixes are originated by AS43404 (i.e., AS43404 is at the end of the AS path) in both IPv4 and IPv6 on March 16, 2024.

import pybgpstream

TARGET_AS = "43404"

FROM_TIME = "2024-03-16 00:00:00"
UNTIL_TIME = "2024-03-16 23:59:59"

def get_orig_prefixes(ip_version_filter):
    stream = pybgpstream.BGPStream(
        from_time=FROM_TIME,
        until_time=UNTIL_TIME,
        record_type="ribs",
        filter=f"ipversion {ip_version_filter}",
    )

    prefixes = set()

    for rec in stream.records():
        for elem in rec:
            aspath = elem.fields.get("as-path")
            if not aspath:
                continue

            ases = aspath.split()
            if not ases:
                continue

            # Origin AS = last AS in the AS path
            if ases[-1] != TARGET_AS:
                continue

            pfx = elem.fields.get("prefix")
            if pfx:
                prefixes.add(pfx)

    return prefixes


v4_prefixes = get_orig_prefixes(4)
v6_prefixes = get_orig_prefixes(6)

print("IPv4 prefixes originated by AS{} on 2024-03-16:".format(TARGET_AS))
for p in sorted(v4_prefixes):
    print(p)

print("\nIPv6 prefixes originated by AS{} on 2024-03-16:".format(TARGET_AS))
for p in sorted(v6_prefixes):
    print(p)
