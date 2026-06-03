# Rank the vantage points based on the number of updates they collected during the time period from 9:30 PM on March 1, 2024 to 5:39 AM on March 2, 2024.

import pybgpstream
from collections import defaultdict

FROM_TIME = "2024-03-01 21:30:00"
UNTIL_TIME = "2024-03-02 05:39:00"

# All collectors, updates only
stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="updates",
)

# Count updates per VP (peer_address)
counts = defaultdict(int)

for rec in stream.records():
    for elem in rec:
        if elem.type in ("A", "W"):
            vp = elem.peer_address
            if vp is not None:
                counts[vp] += 1

# Sort by descending update count
ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)

for vp, count in ranked:
    print(f"{vp}: {count}")
