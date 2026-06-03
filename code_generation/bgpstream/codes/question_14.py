# Did the last AS in the AS paths for prefix 2804:5704::/32 changed between March 1 5:00, 2024 and March 21 9:00, 2024? Consider only the VPs babe:ab13:9ec6:b88d:5b6a:5729:1570:576f, a35:86c4:162e:4a1b:202b:dc58:82a:1cca, 74.255.240.36, 204.209.198.79, 103.52.15.204, 143.192.143.111, 50.188.246.246, and 238:81a9:96a4:2939:bac2:87e7:251b:d58d.

#!/usr/bin/env python

import pybgpstream

PREFIX = "2804:5704::/32"

T1_FROM = "2024-03-01 05:00:00"
T1_UNTIL = "2024-03-01 05:00:00"

T2_FROM = "2024-03-21 09:00:00"
T2_UNTIL = "2024-03-21 09:00:00"

VP_IPS = {
    "babe:ab13:9ec6:b88d:5b6a:5729:1570:576f",
    "a35:86c4:162e:4a1b:202b:dc58:82a:1cca",
    "74.255.240.36",
    "204.209.198.79",
    "103.52.15.204",
    "143.192.143.111",
    "50.188.246.246",
    "238:81a9:96a4:2939:bac2:87e7:251b:d58d",
}

def get_origins(from_time, until_time):
    stream = pybgpstream.BGPStream(
        from_time=from_time,
        until_time=until_time,
        record_type="ribs",
        filter=f"ipversion 6 and prefix exact {PREFIX}",
    )

    vp_origins = {vp: set() for vp in VP_IPS}

    for rec in stream.records():
        for elem in rec:
            if elem.peer_address not in VP_IPS:
                continue

            aspath = elem.fields.get("as-path")
            if not aspath:
                continue

            ases = aspath.split()
            if not ases:
                continue

            origin = ases[-1]
            vp_origins[elem.peer_address].add(origin)

    return vp_origins

orig1 = get_origins(T1_FROM, T1_UNTIL)
orig2 = get_origins(T2_FROM, T2_UNTIL)

changed = False

for vp in sorted(VP_IPS):
    o1 = orig1.get(vp, set())
    o2 = orig2.get(vp, set())
    vp_changed = (o1 != o2)
    if vp_changed:
        changed = True
    print(f"VP {vp}: origins@T1={o1 or 'None'} origins@T2={o2 or 'None'} changed={vp_changed}")

print("\nAny VP changed:", changed)
