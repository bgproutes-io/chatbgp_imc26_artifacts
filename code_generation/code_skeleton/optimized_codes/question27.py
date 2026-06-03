from pyXoXapi import *
import os
import json
from datetime import datetime


answer_file = "../../evaluation/eval_results/OP/answer27.json"
size = 0
time = 0

bogon_prefixes = set()
bgp2go = set()
# Source: https://bgpfilterguide.nlnog.net/guides/bogon_prefixes/
# Source: https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml
# Source: https://www.iana.org/assignments/iana-ipv6-special-registry/iana-ipv6-special-registry.xhtml
bogon_prefixes_list = [
    ("=", "0.0.0.0/8"),          # RFC 1122 ‘this’ network
    ("=", "0.0.0.0/32"),          # This host on this network
    ("=", "10.0.0.0/8"),         # RFC 1918 private space
    ("=", "100.64.0.0/10"),      # RFC 6598 Carrier grade nat space
    ("=", "127.0.0.0/8"),        # RFC 1122 localhost
    ("<<=", "169.254.0.0/16"),     # RFC 3927 link local
    ("=", "172.16.0.0/12"),      # RFC 1918 private space
    ("<<=", "192.0.2.0/24"),       # RFC 5737 TEST-NET-1
    ("<<=", "192.0.0.0/24"),       # IETF Protocol Assignments
    ("=", "192.0.0.8/32"),       # IPv4 dummy address
    ("=", "192.0.0.170/32"),       # NAT64/DNS64 Discovery
    ("=", "192.0.0.171/32"),       # NAT64/DNS64 Discovery
    ("<<=", "192.168.0.0/16"),     # RFC 1918 private space
    ("<<=", "192.88.99.0/24"),     # RFC 7526 6to4 anycast relay
    ("=", "198.18.0.0/15"),      # RFC 2544 benchmarking
    ("<<=", "198.51.100.0/24"),    # RFC 5737 TEST-NET-2
    ("<<=", "203.0.113.0/24"),     # RFC 5737 TEST-NET-3
    ("=", "224.0.0.0/4"),        # multicast
    ("=", "240.0.0.0/4"),        # reserved
    ("=", "255.255.255.255/32"),        # Limited Broadcast
 
    ("=", "::/128"),             # unspecified
    ("=", "::1/128"),            # loopback
    ("<<=", "::ffff:0:0/96"),      # IPv4-mapped
    ("<<=", "64:ff9b:1::/48"),      # IPv4-IPv6 Translat.
    ("<<=", "::/96"),              # deprecated
    ("<<=", "100::/64"),           # RFC 6666 Discard-Only
    ("<<=", "100:0:0:1::/64"),           # Dummy IPv6 Prefix
    ("<<=", "2001:2::/48"),       # RFC 5180 Benchmarking
    ("=", "2001::/23"),       # IETF Protocol Assignments
    #("<<=", "2001::/32"),       # TEREDO
    ("=", "2001:10::/28"),       # RFC 4843 Deprecated (previously ORCHID)
    #("=", "2002::/16"),       # RFC3056 6to4
    #("<<=", "2620:4f:8000::/48"),       # Direct Delegation AS112 Service
    ("=", "3ffe::/16"),       # RFC 3701 old 6bone
    ("=", "3fff::/20"),       # RFC 9637 documentation
    ("=", "5f00::/16"),       # RFC 9602 SRv6 SIDs
    ("<<=", "2001:db8::/32"),      # RFC 3849 documentation
    ("=", "fc00::/7"),           # RFC 4193 unique local unicast
    ("=", "fe80::/10"),          # RFC 4291 link local unicast
    ("=", "fec0::/10"),          # RFC 3879 old site local unicast
    ("=", "ff00::/8"),           # RFC 4291 multicast
]

selected_vantage_points = get_vantage_points(
    vp_ips=param_vp, 
    data_afi = param_ip_protocol,
    ) 

for vantage_point in selected_vantage_points:
  
    rib_data = get_rib(
        [vantage_point], 
        date = param_time, 
        return_community = False,
        aspath_regexp='(^| )'+str(param_asx)+'$',
        prefix_filter=bogon_prefixes_list, 
        details = True,
        ) 

    bgp_data = rib_data.get("data", {}).get("bgp", {})
    time_info = rib_data.get("seconds")
    size_info = rib_data.get("bytes")
    
    size += size_info or 0
    time += time_info or 0
    
    # For every asn in the AS path.
    for vp_id, prefix_data in bgp_data.items():
        
        
        for prefix in prefix_data.keys():
            bogon_prefixes.add(prefix)
            bgp2go.add(vantage_point.ip)
            
output = {
    "time": time,
    "size": size,
    "final_answer": len(bogon_prefixes),
    "bgp2go":list(bgp2go)
}

os.makedirs(os.path.dirname(answer_file), exist_ok=True)

with open(answer_file, "w") as f:
    json.dump(output, f, indent=2)

