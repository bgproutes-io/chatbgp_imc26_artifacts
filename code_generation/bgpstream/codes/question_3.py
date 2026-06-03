# What are the neighboring autonomous systems of AS33893 in IPv4?

import pybgpstream
from collections import defaultdict

# Create a BGPStream instance
stream = pybgpstream.BGPStream(
    from_time="2023-01-01 00:00:00", until_time="2023-01-02 00:00:00",
    record_type="ribs",
    filter="ipversion 4 and aspath ^.*_33893_.*$"
)

# Create a set to store neighboring ASes
neighboring_as = set()

# Get records and elems
for rec in stream.records():
    for elem in rec:
        # Get the AS path and split into ASNs
        ases = elem.fields["as-path"].split()

        # Find the index of AS33893 and add its neighbors to the set
        for index, asn in enumerate(ases):
            if asn == "33893":
                # If ASN is found, add the previous and next ASN in the path
                if index > 0:
                    neighboring_as.add(ases[index - 1])
                if index < len(ases) - 1:
                    neighboring_as.add(ases[index + 1])

# Print the neighboring ASes
print("Neighboring ASes of AS33893:", neighboring_as)