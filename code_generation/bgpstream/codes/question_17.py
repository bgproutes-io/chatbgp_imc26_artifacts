# For every VP, can you provide the number of announcements received every hour from 06:00 on March 22, 2024, through 00:00 on March 30, 2024?

#!/usr/bin/env python

import pybgpstream
from collections import defaultdict
from datetime import datetime, timedelta, timezone

# Time window (UTC)
START_DT = datetime(2024, 3, 22, 6, 0, 0, tzinfo=timezone.utc)
END_DT   = datetime(2024, 3, 30, 0, 0, 0, tzinfo=timezone.utc)

FROM_TIME = START_DT.strftime("%Y-%m-%d %H:%M:%S")
UNTIL_TIME = END_DT.strftime("%Y-%m-%d %H:%M:%S")

# Total number of 1-hour buckets
NUM_HOURS = int((END_DT - START_DT).total_seconds() // 3600)

# BGPStream: all collectors, updates only, full IP space (v4+v6)
stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    record_type="updates",
)

# (vp, hour_index) -> count
counts = defaultdict(int)

start_ts = int(START_DT.timestamp())
end_ts = int(END_DT.timestamp())

for rec in stream.records():
    # rec.time is Unix timestamp (int, UTC)
    if rec.time < start_ts or rec.time >= end_ts:
        continue

    for elem in rec:
        # Only announcements
        if elem.type != "A":
            continue

        vp = elem.peer_address
        if not vp:
            continue

        # Bucket index for this record
        hour_idx = (rec.time - start_ts) // 3600
        if 0 <= hour_idx < NUM_HOURS:
            counts[(vp, hour_idx)] += 1

# Collect all VPs seen
vps = sorted({vp for (vp, _) in counts.keys()})

# Output as CSV: vp,hour_start_iso,count
print("vp,hour_start,count")

for vp in vps:
    for hour_idx in range(NUM_HOURS):
        bucket_start = START_DT + timedelta(hours=hour_idx)
        key = (vp, hour_idx)
        cnt = counts.get(key, 0)
        print("{},{},{}".format(
            vp,
            bucket_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            cnt,
        ))
