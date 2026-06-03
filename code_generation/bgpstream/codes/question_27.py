# How many bogon prefixes are announced by AS 43404 in both IPv4 and IPv6.

#!/usr/bin/env python

import pybgpstream
import ipaddress

TARGET_AS = "43404"

# Common IPv4 and IPv6 bogon ranges
BOGON_NETS = [
    # IPv4 bogons
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    # IPv6 bogons
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("::ffff:0:0/96"),
    ipaddress.ip_network("64:ff9b::/96"),
    ipaddress.ip_network("100::/64"),
    ipaddress.ip_network("2001:2::/48"),
    ipaddress.ip_network("2001:10::/28"),
    ipaddress.ip_network("2001:db8::/32"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("ff00::/8"),
]

def is_bogon(prefix):
    try:
        net = ipaddress.ip_network(prefix, strict=False)
    except:
        return False
    for b in BOGON_NETS:
        if net.subnet_of(b):
            return True
    return False


def count_bogons(ipver):
    stream = pybgpstream.BGPStream(
        record_type="ribs",
        filter=f"ipversion {ipver}",
    )

    seen = set()

    for rec in stream.records():
        for elem in rec:
            print (elem)
            aspath = elem.fields.get("as-path")
            if not aspath:
                continue

            ases = aspath.split()
            if not ases or ases[-1] != TARGET_AS:
                continue

            pfx = elem.fields.get("prefix")
            if not pfx:
                continue

            if is_bogon(pfx):
                seen.add(pfx)

    return seen


v4 = count_bogons(4)
v6 = count_bogons(6)

print("IPv4 bogon prefixes originated by AS43404:", len(v4))
for p in sorted(v4):
    print(" ", p)

print("\nIPv6 bogon prefixes originated by AS43404:", len(v6))
for p in sorted(v6):
    print(" ", p)
