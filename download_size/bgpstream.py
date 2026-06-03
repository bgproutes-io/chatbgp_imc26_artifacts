from pathlib import Path
import json

DATE = "20260520"
NUMBER_OF_VPS = 10

LONG_TIMEFRAME_DAYS = 30
SHORT_TIMEFRAME_DAYS = 10

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "target_path/bgptables"

OUTPUT_PATH = BASE_DIR

BASELINE_FILE = BASE_DIR / f"../question_generator/baseline_metrics_{NUMBER_OF_VPS}.json"

with open(BASELINE_FILE, "r", encoding="utf-8") as f:
    baseline_data = json.load(f)

VP_IPs = baseline_data["vantage_points"]

directory_cache = {}

# =====================================================
# DIRECTORY CACHE
# =====================================================

def get_directory_listing(url):

    if url in directory_cache:
        return directory_cache[url]

    try:

        result = subprocess.check_output(
            ["curl", "-s", url],
            text=True
        )

        directory_cache[url] = result

        return result

    except Exception:

        return ""

# =====================================================
# SIZE CONVERSION
# =====================================================

def convert_to_mb(size_str):

    size_str = size_str.strip().upper()

    if size_str.endswith("K"):
        return float(size_str[:-1]) / 1024

    elif size_str.endswith("M"):
        return float(size_str[:-1])

    elif size_str.endswith("G"):
        return float(size_str[:-1]) * 1024

    return 0.0

# =====================================================
# RIB SIZE (single date)
# =====================================================

def get_rib_size(collector,date):

    year = date[:4]
    month = date[4:6]
    day = date[6:8]

    try:

        if collector.startswith("rrc"):

            url = (f"https://data.ris.ripe.net/"f"{collector}/{year}.{month}/")

            pattern = (rf"bview\.{year}{month}{day}\.0000\.gz"rf".*?([0-9\.]+[KMG])")

        else:

            url = (f"http://archive.routeviews.org/"f"{collector}/bgpdata/"f"{year}.{month}/RIBS/")

            pattern = (rf"rib\.{year}{month}{day}\.0000\.bz2"rf".*?([0-9\.]+[KMG])")

        html = get_directory_listing(url)

        matches = re.findall(pattern,html,re.DOTALL)

        return round(sum(convert_to_mb(x)for x in matches),2) # Size download size from Collector in MB 

    except Exception:

        return 0.0

# =====================================================
# UPDATE SIZE (INTERVAL)
# =====================================================

def get_updates_size(collector,start_date,end_date):

    start_dt = datetime.strptime(start_date,"%Y%m%d")

    end_dt = datetime.strptime(end_date,"%Y%m%d")

    total_mb = 0.0

    current_dt = start_dt

    while current_dt <= end_dt:

        date = current_dt.strftime("%Y%m%d")

        year = date[:4]
        month = date[4:6]
        day = date[6:8]

        try:

            if collector.startswith("rrc"):

                url = (f"https://data.ris.ripe.net/"f"{collector}/{year}.{month}/")

                pattern = (rf"updates\.{year}{month}{day}\.\d+\.gz"rf".*?([0-9\.]+[KMG])")

            else:

                url = (f"http://archive.routeviews.org/"f"{collector}/bgpdata/"f"{year}.{month}/UPDATES/")

                pattern = (rf"updates\.{year}{month}{day}\.\d+\.bz2"rf".*?([0-9\.]+[KMG])")

            html = get_directory_listing(url)

            matches = re.findall(pattern,html,re.DOTALL)

            for size_str in matches:

                total_mb += convert_to_mb(size_str)

        except Exception as e:
            print(e)

        current_dt += timedelta(days=1)

    return round(total_mb,2)

# =====================================================
# TIMEFRAME AGGREGATION
# =====================================================

def get_timeframe_sizes(collectors,end_date,days):

    total_rib = 0.0
    total_updates = 0.0

    end_dt = datetime.strptime(end_date,"%Y%m%d")

    for i in range(days):

        current = (end_dt - timedelta(days=i)).strftime("%Y%m%d")

        for collector in collectors:

            total_rib += get_rib_size(collector,current)

            total_updates += get_updates_size(collector,current,current)

    return (round(total_rib, 2),round(total_updates, 2))

# =====================================================
# MAP VPS TO COLLECTORS
# =====================================================

def map_vp_to_collectors(date,target_vps):

    results = []

    collector_cache = {}

    csv_files = glob.glob(
        str(DATA_PATH /date/"*.csv"))

    for csv_file in csv_files:

        collector = Path(csv_file).stem

        if collector.startswith("vp_"):
            continue

        if collector not in collector_cache:

            collector_cache[collector] = {"RIB":get_rib_size(collector,date),"UPDATE":get_updates_size(collector,date,date)}
            
        try:

            chunks = pd.read_csv(csv_file,chunksize=100000)

            for chunk in chunks:

                if "Probe" in chunk.columns:

                    chunk = chunk.rename(columns={"Probe":"Collector"})

                filtered = chunk[chunk["IP"].isin(target_vps)]

                filtered = filtered.drop_duplicates(subset=["IP"])

                for _, row in filtered.iterrows():

                    results.append({"VP_IP":row["IP"],"Collector":collector,"RIB_Size_MB":collector_cache[collector]["RIB"],"UPDATE_Size_MB":collector_cache[collector]["UPDATE"]})

        except Exception:
            pass
    return pd.DataFrame(results)

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    
    df = map_vp_to_collectors(DATE,VP_IPs)
    
    if df.empty:
        print("No collectors matched provided VPs")
        exit()
    
    unique_collectors = df.drop_duplicates(subset=["Collector"])
    
    collector_names = unique_collectors["Collector"].unique()
    
    rib_30d, upd_30d = get_timeframe_sizes(collector_names,DATE,LONG_TIMEFRAME_DAYS)
    
    _, upd_10d = get_timeframe_sizes(collector_names,DATE,SHORT_TIMEFRAME_DAYS)
    
    df["TOTAL_UNIQUE_RIB_30D_MB"] = rib_30d
    
    df["TOTAL_UNIQUE_UPDATES_30D_MB"] = upd_30d
    
    df["TOTAL_UNIQUE_UPDATES_10D_MB"] = upd_10d
    
    OUTPUT_PATH.mkdir(parents=True,exist_ok=True)
    df.to_csv(OUTPUT_PATH/"bgpstream.csv",index=False)