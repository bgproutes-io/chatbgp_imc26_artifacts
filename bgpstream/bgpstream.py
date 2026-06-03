import pybgpstream
import os
import time

CACHE_DIR = "/tmp/bgp-cache"

FROM_TIME = "2026-05-17 00:00:00"
UNTIL_TIME = "2025-05-17 23:59:59"

COLLECTORS = ["route-views2"]

# Optional:
# Set to None if you don't want filtering
PEER_IP = "203.123.48.6"

def get_dir_size(path):
    total = 0

    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)

            if os.path.isfile(fp):
                total += os.path.getsize(fp)

    return total

# Size before download
before_size = get_dir_size(CACHE_DIR) if os.path.exists(CACHE_DIR) else 0

stream = pybgpstream.BGPStream(
    from_time=FROM_TIME,
    until_time=UNTIL_TIME,
    collectors=COLLECTORS,
    record_type="updates",
)

# Enable cache
stream.set_data_interface_option(
    "broker",
    "cache-dir",
    CACHE_DIR
)

record_count = 0
elem_count = 0

start = time.time()

for elem in stream:

    # Filter by peer IP if needed
    if PEER_IP is not None:
        if elem.peer_address != PEER_IP:
            continue

    elem_count += 1

    if elem_count % 10000 == 0:
        print(f"Processed {elem_count} elems")

end = time.time()

# Size after download
after_size = get_dir_size(CACHE_DIR)

downloaded_bytes = after_size - before_size

print("\n===== Statistics =====")
print(f"Elements processed: {elem_count}")
print(f"Downloaded data: {downloaded_bytes / (1024*1024):.2f} MB")
print(f"Execution time: {end - start:.2f} seconds")