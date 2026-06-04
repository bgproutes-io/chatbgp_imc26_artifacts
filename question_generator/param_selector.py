import json
import random
from collections import defaultdict
from pathlib import Path
# =========================================================
# CONFIGURATION
# =========================================================
NUMBER_OF_VPS = 10

BASE_DIR = Path(__file__).resolve().parent

DATASET_FILE = BASE_DIR / f"param_dataset{NUMBER_OF_VPS}.jsonl"

# Fixed seed for reproducibility
RANDOM_SEED = 13

# Maximum stored observations per VP per structure
# Prevents unlimited memory growth while preserving
# approximate frequency distributions
MAX_ITEMS_PER_VP = 10000

random.seed(RANDOM_SEED)
# =========================================================
# GLOBAL DATA
# =========================================================

# Single timestamp extracted from dataset
time = ""

# Update interval extracted from dataset
time_interval = ""

# Stores tuples:
# (VP address, IP protocol)
vantage_points = set()

# Frequency-preserving structures
# Lists intentionally retained
vp_asns = defaultdict(list)

vp_middle_asns = defaultdict(list)

vp_pairs = defaultdict(list)

vp_prefixes = defaultdict(list)

vp_origin_asns = defaultdict(list)

vp_prefix_asn = defaultdict(list)

vp_communities = defaultdict(list)

vp_prefix_with_communities = defaultdict(list)

# VP categories used for filtering
withdrawal_vps = set()

update_vps = set()

black_vps = set()

large_vps = set()

prepend_vps = set()

ipv4_vps = set()

ipv6_vps = set()

# (community ASN, vp)
community_asx = defaultdict(list)

# =========================================================
# MEMORY SAFE APPEND
# =========================================================

def bounded_append(container, key, value):

    """
    Reservoir-style bounded storage.

    Preserves list semantics and approximate
    frequency distribution while limiting memory.
    """

    lst = container[key]

    current_size = len(lst)

    # Fill until capacity
    if current_size < MAX_ITEMS_PER_VP:
        lst.append(value)
        return

    # Replace uniformly
    replace_idx = random.randint(0,current_size)

    if replace_idx < MAX_ITEMS_PER_VP:
        lst[replace_idx] = value
        
# =========================================================
# LOAD DATASET
# =========================================================
with open(DATASET_FILE) as f:

    for line in f:

        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue

        vp = row["v"]
        ip = row["ip"]
        prefix = row["p"]
        path = row["a"]
        communities = row.get("c", [])
        vantage_points.add((vp, ip))
        time = time or row["t"]
        time_interval = time_interval or row["ti"]
        
        # -------------------------------------------------
        # PREFIXES
        # -------------------------------------------------
        bounded_append(vp_prefixes,vp,prefix)

        if ":" in prefix:
            ipv6_vps.add(vp)
        else:
            ipv4_vps.add(vp)
        # -------------------------------------------------
        # UPDATE TYPES
        # -------------------------------------------------
        if row["u"] == "W":
            withdrawal_vps.add(vp)
        if row["u"] in ("A", "W"):
            update_vps.add(vp)
        # -------------------------------------------------
        # AS PATH PROCESSING
        # -------------------------------------------------
        unique_asns = list(dict.fromkeys(path))
        for asn in unique_asns:
            bounded_append(vp_asns,vp,asn)
            bounded_append(vp_prefix_asn,vp,(prefix, asn))

        if unique_asns:
            bounded_append(vp_origin_asns,vp,unique_asns[-1])

        if len(unique_asns) >= 3:
            a, b = random.sample(unique_asns[1:],2)
            
            bounded_append(vp_pairs,vp,(a, b))

        for asn in unique_asns[1:-1]:
            bounded_append(vp_middle_asns,vp,asn)
        # ------------------------------------------------
        # PREPENDING DETECTION
        # -------------------------------------------------
        for i in range(len(path) - 1):

            if path[i] == path[i + 1]:
                prepend_vps.add(vp)
                break

        # -------------------------------------------------
        # COMMUNITY PROCESSING
        # -------------------------------------------------
        black_found = False
        large_found = False
        if communities:
            bounded_append(vp_prefix_with_communities,vp,prefix)

        for c in communities:
            bounded_append(vp_communities,vp,c)
            parts = c.lower().split(":")
            
            if len(parts) >= 2 and parts[0].isdigit():
                bounded_append(community_asx,vp,parts[0])

            if c == "65535:666":
                black_found = True
                
            if len(parts) == 3:
                large_found = True
                
        if black_found:
            black_vps.add(vp)

        if large_found:
            large_vps.add(vp)

vantage_points = list(vantage_points)
# =========================================================
# HELPERS
# =========================================================

def random_vps(n=2,allowed_vps=None,include_ip=True):

    candidates = [(vp, ip) for vp, ip in vantage_points if allowed_vps is None or vp in allowed_vps]
    if not candidates:
        return {"vp": "","ip_protocol": ""}

    selected = random.sample(candidates,min(n, len(candidates)))

    d = {"vp": ",".join(vp for vp, _ in selected)}

    if include_ip:
        ips = {ip for _, ip in selected}
        
        d["ip_protocol"] = (ips.pop() if len(ips) == 1 else "")
    return d

def vp_list(d):
    return d["vp"].split(",")


def pick_asn(vps, source):
    values = [asn for vp in vps for asn in source[vp]]

    return str(random.choice(values)) if values else ""

def pick_pair(vps):
    values = [pair for vp in vps for pair in vp_pairs[vp]]
    
    if not values:
        return ""
    a, b = random.choice(values)
    return f"{a},{b}"


def pick_prefix(vps,source=vp_prefixes):

    values = [prefix for vp in vps for prefix in source[vp]]
    return random.choice(values) if values else ""

def add_time(d):
    d["time"] = time

def add_time_interval(d):
    d["time_interval"] = time_interval

# =========================================================
# QUESTIONS
# =========================================================
def question1(n):
    d = random_vps(n)
    add_time(d)
    return d

def question2(n):
    d = random_vps(n)
    add_time(d)
    return d

def question3(n):
    d = random_vps(n)
    add_time(d)
    d["asx"] = pick_asn(vp_list(d), vp_asns)
    return d

def question4(n):
    d = random_vps(n)
    add_time(d)
    return d

def question5(n):
    d = random_vps(n)
    add_time(d)
    d["asxy"] = pick_pair(vp_list(d))
    return d

def question6(n):
    d = random_vps(n)
    add_time(d)
    d["asxy"] = pick_pair(vp_list(d))
    return d

def question7(n):
    d = random_vps(n)
    add_time(d)
    d["asx"] = pick_asn(vp_list(d), vp_middle_asns)
    return d

def question8(n):
    d = random_vps(n)
    add_time(d)
    return d

def question9(n):
    d = random_vps(n)
    add_time(d)
    return d

def question10(n):
    d = random_vps(n)
    d["asx"] = pick_asn(vp_list(d), vp_asns)
    return d

def question11(n):
    d = random_vps(n)
    d["asxy"] = pick_pair(vp_list(d))
    return d

def question12(n):
    d = random_vps(n)
    d["prefix"] = pick_prefix(vp_list(d))
    return d

def question13(n):
    d = random_vps(n)
    d["asxy"] = pick_pair(vp_list(d))
    return d

def question14(n):
    d = random_vps(n, include_ip=False)
    add_time_interval(d)
    d["prefix"] = pick_prefix(vp_list(d))
    return d

def question15(n):
    d = random_vps(n,allowed_vps=withdrawal_vps,include_ip=False)
    add_time_interval(d)
    return d


def question16(n):
    d = random_vps(n,allowed_vps=update_vps,include_ip=False)
    add_time_interval(d)
    return d


def question17(n):
    d = random_vps(n,allowed_vps=update_vps,include_ip=False)
    add_time_interval(d)
    return d

def question18(n):
    d = random_vps(n,allowed_vps=black_vps,include_ip=False)
    add_time_interval(d)
    return d

def question19(n):
    valid_vps = {vp for vp in vp_communities if vp_communities[vp]}
    d = random_vps(n,allowed_vps=valid_vps,include_ip=False)
    add_time_interval(d)
    vps = vp_list(d)
    communities = list({c for vp in vps for c in vp_communities[vp]})
    k = random.randint(1, min(3, len(communities)))
    d["community_set"] = ",".join(random.sample(communities, k))
    return d

def question20(n):
    d = random_vps(n, include_ip=False)
    add_time_interval(d)
    d["asx"] = pick_asn(vp_list(d), vp_asns)
    return d

def question21(n):
    d = random_vps(n,allowed_vps=large_vps,include_ip=False)
    add_time_interval(d)
    return d

def question22(n):
    d = random_vps(n)
    add_time(d)
    return d

def question23(n):
    d = random_vps(n)
    add_time_interval(d)
    d["prefix"] = pick_prefix(vp_list(d))
    return d

def question24(n):
    d = random_vps(n, include_ip=False)
    add_time(d)
    vps = vp_list(d)
    values = [entry for vp in vps for entry in vp_prefix_asn[vp]]
    prefix, asn = random.choice(values)
    d["prefix"] = prefix
    d["asx"] = str(asn)
    return d

def question25(n):
    d = random_vps(n, include_ip=False)
    add_time(d)
    d["prefix"] = pick_prefix(vp_list(d))
    return d

def question26(n):
    d = random_vps(n, include_ip=False)
    add_time(d)
    d["prefix"] = pick_prefix(vp_list(d))
    return d

def question27(n):
    d = random_vps(n)
    add_time(d)
    d["asx"] = pick_asn(vp_list(d), vp_asns)
    return d

def question28(n):
    d = random_vps(n, include_ip=False)
    add_time_interval(d)
    d["asx"] = pick_asn(vp_list(d), vp_origin_asns)
    return d

def question29(n):
    dual_stack_vps = ipv4_vps & ipv6_vps
    d = random_vps(n,allowed_vps=dual_stack_vps,include_ip=False)
    add_time(d)
    return d

def question30(n):
    valid_vps = ipv4_vps
    d = random_vps(n,allowed_vps=valid_vps)
    add_time(d)
    values = [asn for vp in vp_list(d) for asn in vp_origin_asns[vp]]
    d["asx"] = str(random.choice(values))
    return d

def question31(n):
    d = random_vps(n, include_ip=False)
    add_time(d)
    return d

def question32(n):
    d = random_vps(n, include_ip=False)
    add_time(d)
    vps = vp_list(d)
    values = [asn for vp in vps for asn in community_asx[vp]]
    d["asx"] = str(random.choice(values))
    return d

def question33(n):
    d = random_vps(n,allowed_vps=prepend_vps,include_ip=False)
    add_time(d)
    return d

def question34(n):
    d = random_vps(n, include_ip=False)
    add_time(d)
    d["asx"] = pick_asn(vp_list(d), vp_asns)
    return d

def question35(n):
    d = random_vps(n)
    add_time(d)
    d["asxy"] = pick_pair(vp_list(d))
    return d

def question36(n):
    d = random_vps(n, include_ip=False)
    add_time_interval(d)
    return d

def question37(n):
    d = random_vps(n)
    add_time(d)
    d["asx"] = pick_asn(vp_list(d), vp_origin_asns)
    return d

def question38(n):
    d = random_vps(n)
    add_time(d)
    return d

def question39(n):
    d = random_vps(n, include_ip=False)
    add_time(d)
    d["prefix"] = pick_prefix(vp_list(d),vp_prefix_with_communities)
    return d

QUESTION_FUNCTIONS = {
    1: question1,
    2: question2,
    3: question3,
    4: question4,
    5: question5,
    6: question6,
    7: question7,
    8: question8,
    9: question9,
    10: question10,
    11: question11,
    12: question12,
    13: question13,
    14: question14,
    15: question15,
    16: question16,
    17: question17,
    18: question18,
    19: question19,
    20: question20,
    21: question21,
    22: question22,
    23: question23,
    24: question24,
    25: question25,
    26: question26,
    27: question27,
    28: question28,
    29: question29,
    30: question30,
    31: question31,
    32: question32,
    33: question33,
    34: question34,
    35: question35,
    36: question36,
    37: question37,
    38: question38,
    39: question39,
}