import os
import re
import glob
import subprocess
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta

DATE = "20260520" # Date being used in Question

QUESTION_PATH = Path("../evaluation/eval_results/OP/") # Path for the VPs return data for questions

DATA_PATH = Path("./target_path/bgptables") # Path for VP_IP:Collector .CSV FILES

OUTPUT_PATH = Path("./")
# =========================================================
# GLOBAL CACHE
# =========================================================
SIZE_CACHE = {}

def get_timeframe_sizes(
    collectors,
    end_date,
    days
):

    total_rib_mb = 0.0
    total_updates_mb = 0.0

    end_dt = datetime.strptime(
        end_date,
        "%Y%m%d"
    )

    for i in range(days):

        current_dt = end_dt - timedelta(days=i)

        current_date = current_dt.strftime(
            "%Y%m%d"
        )

        for collector in collectors:

            try:

                cache_key = (
                    collector,
                    current_date
                )

                # =====================================
                # CACHE LOOKUP
                # =====================================

                if cache_key not in SIZE_CACHE:

                    rib_size = get_rib_size(
                        collector,
                        current_date
                    )

                    updates_size = get_updates_size(
                        collector,
                        current_date
                    )

                    SIZE_CACHE[cache_key] = {
                        "rib": rib_size,
                        "updates": updates_size
                    }

                total_rib_mb += (
                    SIZE_CACHE[cache_key]["rib"]
                )

                total_updates_mb += (
                    SIZE_CACHE[cache_key]["updates"]
                )

            except Exception as e:

                print(
                    f"Timeframe error "
                    f"{collector} {current_date}"
                )

                print(e)

    return (
        round(total_rib_mb, 2),
        round(total_updates_mb, 2)
    )


def get_directory_listing(url):

    try:

        cmd = f'curl -s "{url}"'

        result = subprocess.check_output(
            cmd,
            shell=True,
            text=True
        )

        return result

    except Exception as e:

        print(f"Error fetching URL: {url}")

        print(e)

        return ""


def convert_to_mb(size_str):

    size_str = size_str.strip().upper()

    if size_str.endswith("K"):
        return float(size_str[:-1]) / 1024

    if size_str.endswith("M"):
        return float(size_str[:-1])

    if size_str.endswith("G"):
        return float(size_str[:-1]) * 1024

    return 0.0


def get_rib_size(collector, date):

    year = date[:4]
    month = date[4:6]
    day = date[6:8]

    total_mb = 0.0

    try:

        # =====================================================
        # RIPE RIS
        # =====================================================

        if collector.startswith("rrc"):

            url = (
                f"https://data.ris.ripe.net/"
                f"{collector}/{year}.{month}/"
            )

            html = get_directory_listing(url)

            pattern = (
                rf'bview\.{year}{month}{day}\.0000\.gz'
                rf'.*?([0-9\.]+[KMG])'
            )

        # =====================================================
        # ROUTEVIEWS
        # =====================================================

        else:

            url = (
                f"http://archive.routeviews.org/"
                f"{collector}/bgpdata/"
                f"{year}.{month}/RIBS/"
            )

            html = get_directory_listing(url)

            pattern = (
                rf'rib\.{year}{month}{day}\.0000\.bz2'
                rf'.*?([0-9\.]+[KMG])'
            )

        matches = re.findall(
            pattern,
            html,
            re.DOTALL
        )

        for size_str in matches:

            total_mb += convert_to_mb(size_str)

        return round(total_mb, 2)

    except Exception as e:

        print(f"RIB ERROR {collector}: {e}")

        return 0.0


def get_updates_size(collector, date):

    year = date[:4]
    month = date[4:6]
    day = date[6:8]

    total_mb = 0.0

    try:

        # =====================================================
        # RIPE RIS
        # =====================================================

        if collector.startswith("rrc"):

            url = (
                f"https://data.ris.ripe.net/"
                f"{collector}/{year}.{month}/"
            )

            pattern = (
                rf'updates\.{year}{month}{day}\.\d+\.gz'
                rf'.*?([0-9\.]+[KMG])'
            )

        # =====================================================
        # ROUTEVIEWS
        # =====================================================

        else:

            url = (
                f"http://archive.routeviews.org/"
                f"{collector}/bgpdata/"
                f"{year}.{month}/UPDATES/"
            )

            pattern = (
                rf'updates\.{year}{month}{day}\.\d+\.bz2'
                rf'.*?([0-9\.]+[KMG])'
            )

        html = get_directory_listing(url)

        matches = re.findall(
            pattern,
            html,
            re.DOTALL
        )

        for size_str in matches:

            total_mb += convert_to_mb(size_str)

        return round(total_mb, 2)

    except Exception as e:

        print(f"UPDATES ERROR {collector}: {e}")

        return 0.0


def map_vp_to_collectors(
    date,
    target_vps
):

    results = []

    csv_files = glob.glob(
        f"{DATA_PATH}/{date}/*.csv"
    )

    print(
        f"\nFound {len(csv_files)} collector files"
    )

    collector_size_cache = {}

    # =====================================================
    # CONVERT TO SET FOR FAST LOOKUP
    # =====================================================

    target_vps = set(target_vps)

    for csv_file in csv_files:

        try:

            collector = os.path.basename(
                csv_file
            ).replace(".csv", "")

            # =================================================
            # SKIP GENERATED FILES
            # =================================================

            if collector.startswith("vp_"):
                continue

            # =================================================
            # READ ONLY REQUIRED COLUMN
            # =================================================

            chunks = pd.read_csv(
                csv_file,
                usecols=["IP"],
                chunksize=100000
            )

            collector_has_target_vp = False

            for chunk in chunks:

                found = chunk[
                    chunk["IP"].isin(target_vps)
                ]

                if not found.empty:

                    collector_has_target_vp = True
                    break

            # =================================================
            # SKIP COLLECTOR IF NO TARGET VPS
            # =================================================

            if not collector_has_target_vp:

                continue

            print(f"\nProcessing {collector}")

            # =================================================
            # LOAD COLLECTOR SIZE ONLY IF NEEDED
            # =================================================

            if collector not in collector_size_cache:

                rib_size = get_rib_size(
                    collector,
                    date
                )

                updates_size = get_updates_size(
                    collector,
                    date
                )

                collector_size_cache[collector] = {
                    "RIB_Size_MB": rib_size,
                    "UPDATE_Size_MB": updates_size
                }

                print(
                    f"RIB={rib_size} MB | "
                    f"UPDATES={updates_size} MB"
                )

            # =================================================
            # RE-READ FULL CSV
            # =================================================

            chunks = pd.read_csv(
                csv_file,
                chunksize=100000
            )

            for chunk in chunks:

                if "Probe" in chunk.columns:

                    chunk = chunk.rename(
                        columns={
                            "Probe": "Collector"
                        }
                    )

                filtered = chunk[
                    chunk["IP"].isin(target_vps)
                ]

                if filtered.empty:
                    continue

                filtered = filtered.drop_duplicates(
                    subset=["IP"]
                )

                for _, row in filtered.iterrows():

                    results.append({
                        "VP_IP": row["IP"],
                        "Collector": collector,
                        "RIB_Size_MB":
                            collector_size_cache[
                                collector
                            ]["RIB_Size_MB"],

                        "UPDATE_Size_MB":
                            collector_size_cache[
                                collector
                            ]["UPDATE_Size_MB"]
                    })

        except Exception as e:

            print(
                f"Error processing "
                f"{csv_file}"
            )

            print(e)

    return pd.DataFrame(results)


def compute_vp_metrics(df, date):

    results = []

    grouped = df.groupby("VP_IP")

    for vp_ip, vp_df in grouped:

        print(
            f"\n================================"
        )

        print(
            f"Computing metrics for VP: "
            f"{vp_ip}"
        )

        print(
            f"================================"
        )

        unique_collectors = vp_df.drop_duplicates(
            subset=["Collector"]
        )

        unique_collector_names = unique_collectors[
            "Collector"
        ].unique()

        # =====================================================
        # CURRENT DAY TOTALS
        # =====================================================

        total_unique_rib = round(
            unique_collectors[
                "RIB_Size_MB"
            ].sum(),
            2
        )

        total_unique_updates = round(
            unique_collectors[
                "UPDATE_Size_MB"
            ].sum(),
            2
        )

        # =====================================================
        # 30 DAY TOTALS
        # =====================================================

        (
            total_rib_30d,
            total_updates_30d
        ) = get_timeframe_sizes(
            unique_collector_names,
            date,
            30
        )

        # =====================================================
        # 10 DAY UPDATE TOTALS
        # =====================================================

        (
            _,
            total_updates_10d
        ) = get_timeframe_sizes(
            unique_collector_names,
            date,
            10
        )

        # =====================================================
        # ADD METRICS
        # =====================================================

        vp_df = vp_df.copy()

        vp_df["TOTAL_UNIQUE_RIB_MB"] = (
            total_unique_rib
        )

        vp_df["TOTAL_UNIQUE_UPDATES_MB"] = (
            total_unique_updates
        )

        vp_df["TOTAL_UNIQUE_RIB_30D_MB"] = (
            total_rib_30d
        )

        vp_df["TOTAL_UNIQUE_UPDATES_30D_MB"] = (
            total_updates_30d
        )

        vp_df["TOTAL_UNIQUE_UPDATES_10D_MB"] = (
            total_updates_10d
        )

        results.append(vp_df)

    return pd.concat(
        results,
        ignore_index=True
    )

if __name__ == "__main__":
    
    all_question_dfs = []
    # =================================================
    # FIND ALL QUESTION FILES
    # =================================================
    optimized_answers = sorted(QUESTION_PATH.glob("answer*.json"))

    # =================================================
    # PROCESS QUESTIONS
    # =================================================

    for ans in optimized_answers:

        filename = ans.name

        match = re.search(r'answer(\d+)\.json',filename)

        question_id = int(match.group(1))
        # =============================================
        # LOAD INCLUDED VPS
        # =============================================

        with open(ans, "r") as f:

            data = json.load(f)

        included_vps = set(data.get("bgp2go",[]))

        if len(included_vps) == 0:
            print("No VPs found, skipping")
            continue
        # =============================================
        # MAP VPS TO COLLECTORS
        # =============================================
        df = map_vp_to_collectors(DATE,included_vps)
        # =============================================
        # SAFETY FILTER
        # =============================================
        df = df[df["VP_IP"].isin(included_vps)]
        
        if df.empty:
            print("Empty dataframe after filtering")
            question_result = {
                "QUESTION_ID": question_id,
                "NUM_VPS": 0,
                "NUM_COLLECTORS": 0,
                "TOTAL_UNIQUE_RIB_MB": 0,
                "TOTAL_UNIQUE_UPDATES_MB": 0,
                "TOTAL_UNIQUE_RIB_30D_MB": 0,
                "TOTAL_UNIQUE_UPDATES_30D_MB": 0,
                "TOTAL_UNIQUE_UPDATES_10D_MB": 0
                }
            all_question_dfs.append(pd.DataFrame([question_result]))
            continue

        # =============================================
        # COMPUTE PER-VP METRICS
        # =============================================
        df = compute_vp_metrics(df,DATE)
            
        unique_collectors = df.drop_duplicates(subset=["Collector"])

        unique_collector_names = unique_collectors["Collector"].unique()
            
        # =====================================================
        # TIMEFRAME TOTALS FOR UNIQUE COLLECTORS
        # =====================================================
            
        (total_rib_30d,total_updates_30d) = get_timeframe_sizes(unique_collector_names,DATE,30)
        (_,total_updates_10d) = get_timeframe_sizes(unique_collector_names,DATE,10)
            
        question_result = {
            "QUESTION_ID": question_id,
            "NUM_VPS":df["VP_IP"].nunique(),
            "NUM_COLLECTORS":unique_collectors["Collector"].nunique(),
            "TOTAL_UNIQUE_RIB_MB":round(unique_collectors["RIB_Size_MB"].sum(),2),
            "TOTAL_UNIQUE_UPDATES_MB":round(unique_collectors["UPDATE_Size_MB"].sum(),2),
            "TOTAL_UNIQUE_RIB_30D_MB":total_rib_30d,
            "TOTAL_UNIQUE_UPDATES_30D_MB":total_updates_30d,
            "TOTAL_UNIQUE_UPDATES_10D_MB":total_updates_10d
            }
            
        all_question_dfs.append(pd.DataFrame([question_result]))

    final_df = pd.concat(all_question_dfs,ignore_index=True)
        
    final_df = final_df.sort_values(by="QUESTION_ID").reset_index(drop=True)

    final_df.to_csv(f"{OUTPUT_PATH}/"f"bgp2go.csv",index=False)