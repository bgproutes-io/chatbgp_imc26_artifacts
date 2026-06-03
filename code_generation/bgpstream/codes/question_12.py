# For each VP, can you write the time of the most recent update for the IPv6 prefix 2a13:df80:8390::/48?

import pybgpstream

PREFIX = "2a13:df80:8390::/48"

# All collectors, all time, IPv6, updates for that exact prefix
stream = pybgpstream.BGPStream(
    record_type="updates",
    filter=f"ipversion 6 and prefix exact {PREFIX}",
)

# peer_address -> most recent update time
latest_update_per_vp = {}

for rec in stream.records():
    for elem in rec:
        # Only BGP updates (announcements/withdrawals)
        if elem.type not in ("A", "W"):
            continue

        vp = elem.peer_address
        if vp is None:
            continue

        t = rec.time
        prev = latest_update_per_vp.get(vp)
        if prev is None or t > prev:
            latest_update_per_vp[vp] = t

# Print most recent update time per VP
for vp in sorted(latest_update_per_vp.keys()):
    print(f"VP {vp}: latest update time = {latest_update_per_vp[vp]}")