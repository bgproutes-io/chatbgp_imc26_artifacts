# At 7:00 AM on March 1st, 2024, what is the proportion of AS paths the contains AS 174?

import pybgpstream

TIME_FROM = "2024-03-01 07:00:00"
TIME_UNTIL = "2024-03-01 07:00:00"

TARGET_AS = "174"

stream = pybgpstream.BGPStream(
    from_time=TIME_FROM,
    until_time=TIME_UNTIL,
    record_type="ribs",
)

total_paths = 0
paths_with_174 = 0

for rec in stream.records():
    for elem in rec:
        aspath = elem.fields.get("as-path")
        if not aspath:
            continue

        ases = aspath.split()
        if not ases:
            continue

        total_paths += 1
        if TARGET_AS in ases:
            paths_with_174 += 1

if total_paths == 0:
    print("No AS paths observed.")
else:
    proportion = paths_with_174 / total_paths
    print("Total AS paths:", total_paths)
    print("Paths containing AS174:", paths_with_174)
    print("Proportion:", proportion)
