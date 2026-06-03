from pyXoXapi import *
import os
import json
import random
import time
import logging
from ipaddress import ip_address
from pathlib import Path
from typing import Dict, List, Any, Optional

# ============================================================
# CONFIGURATION
# ============================================================

DATE = "2026-05-20T00:00:00"

START_DATE = "2026-05-20T00:00:00"
END_DATE = "2026-05-20T23:59:59"

NUMBER_OF_VPS = 10

RANDOM_SEED = 13

RETRY_SLEEP = 300

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_FILE = BASE_DIR / f"param_dataset{NUMBER_OF_VPS}.jsonl"

BASELINE_FILE = BASE_DIR / f"baseline_metrics_{NUMBER_OF_VPS}.json"  

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")

logger = logging.getLogger(__name__)

# ============================================================
# HELPERS
# ============================================================

def safe_int_path(path_str: str) -> List[int]:
    """
    Convert AS path string into integer ASN list.
    """
    return [int(asn) for asn in path_str.split() if asn.isdigit()]

def safe_communities(comm_str: str) -> List[str]:
    """
    Convert community string into list.
    """
    return comm_str.split()

def get_ip_version(ip: str) -> str:

    return "6" if ip_address(ip).version == 6 else "4"

def should_retry(error: str) -> bool:

    error = error.lower()

    retry_patterns = [
        "rate limit",
        "429",
        "too many requests",
        "502 bad gateway",
        "invalid json response",
        "jsondecodeerror",
    ]

    return any(p in error for p in retry_patterns)

def query_with_retry(query_function,*args,retry_sleep: int = RETRY_SLEEP,**kwargs) -> Optional[Dict[str, Any]]:

    while True:
        try:
            response = query_function(*args, **kwargs)
            return response

        except Exception as e:
            msg = str(e)

            if should_retry(msg):

                logger.warning(
                    "Rate limited / transient error: %s",
                    msg
                )

                logger.warning(
                    "Sleeping %s seconds before retry",
                    retry_sleep
                )

                time.sleep(retry_sleep)

                continue

            logger.error("Permanent failure: %s", msg)

            return None

# ============================================================
# METRICS
# ============================================================
metrics = {

    "rib_time": 0,
    "rib_size": 0, # RIB Size will be used as bgproutes Without Optimization for each date 

    "update_time": 0,
    "update_size": 0, # Update Size will be used as bgproutes Without Optimization for each one day Time Interval 
}


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_DIR.mkdir(parents=True,exist_ok=True)

    random.seed(RANDOM_SEED)

    logger.info("Fetching vantage points")

    vps = get_vantage_points(peering_protocol="bgp", source = ["ris","routeviews"]) # Only RIPE RIS and Routeviwes collector because in bgpstream/bgp2go comparison 

    selected_vps = random.sample(list(vps),NUMBER_OF_VPS)

    logger.info("Selected %s vantage points",len(selected_vps))

    with open(OUTPUT_FILE,"w",encoding="utf-8") as outfile:

        for idx, vp in enumerate(selected_vps,start=1):
            logger.info("[%s/%s] VP=%s",idx,len(selected_vps),vp.ip)
            
            collect_rib(vp,outfile)
            collect_updates(vp,outfile)

    baseline = {
        "num_vps": NUMBER_OF_VPS,
        "vantage_points": [vp.ip for vp in selected_vps],**metrics
        }

    with open(BASELINE_FILE,"w",encoding="utf-8") as bf:
        json.dump(baseline,bf,indent=2,ensure_ascii=False)
        
    logger.info("Finished dataset generation")

# ============================================================
# RIB COLLECTION
# ============================================================

def collect_rib(vp, outfile):

    response = query_with_retry(get_rib,[vp],date=DATE,return_aspath=True,return_community=True,details=True)

    if not response:
        return

    metrics["rib_time"] += response.get("seconds",0) or 0

    metrics["rib_size"] += response.get("bytes",0) or 0

    bgp_data = (response.get("data", {}).get("bgp", {}).get(str(vp.unique_id)))

    if not bgp_data:
        return

    for prefix, data in bgp_data.items():

        entry = {
            "v": vp.ip,
            "t": DATE,
            "p": prefix,
            "a": safe_int_path(data[0]),
            "c": safe_communities(data[1]),
            "ip": get_ip_version(vp.ip),
            "ti": "",
            "ts": "",
            "u": "",
        }
        outfile.write(json.dumps(entry,ensure_ascii=False) + "\n")

# ============================================================
# UPDATE COLLECTION
# ============================================================
def collect_updates(vp, outfile):

    response = query_with_retry(get_updates,[vp],start_date=START_DATE,end_date=END_DATE,return_aspath=True,return_community=True,details=True)

    if not response:
        return

    metrics["update_time"] += response.get("seconds",0) or 0

    metrics["update_size"] += response.get("bytes",0) or 0
    
    update_data = (response.get("data", {}).get("bgp", {}).get(str(vp.unique_id)))

    if not update_data:
        return

    for update in update_data:
        event = update[1]
        if event == "A":
            as_path = safe_int_path(update[3])
            communities = safe_communities(update[4])

        else:
            as_path = []
            communities = []

        entry = {
            "v": vp.ip,
            "t": "",
            "p": update[2],
            "a": as_path,
            "c": communities,
            "ip": get_ip_version(vp.ip),
            "ti": f"{START_DATE} - {END_DATE}",
            "ts": update[0],
            "u": event,
        }
        outfile.write(json.dumps(entry,ensure_ascii=False) + "\n")

if __name__ == "__main__":

    main()