from multiprocessing import Pool
from pathlib import Path
import pandas as pd
import subprocess
from probes_list import probes

# =====================================================
# CONFIGURATION
# =====================================================

DATA_PATH = Path("./target_path")
PROBES = probes
NUM_WORKERS = 10
DATE = "20260527"  #YYYYMMDD
DATA_PATH.mkdir(exist_ok=True)

# =====================================================
# DOWNLOAD SINGLE PROBE
# =====================================================

def download_one_probe(target):

    date, probe = target

    print(f"Downloading {date} from {probe}")

    year = date[:4]
    month = date[4:6]
    day = date[6:8]

    time = "0000"

    if probe.startswith("rrc"):

        url = f"https://data.ris.ripe.net/{probe}/{year}.{month}/bview.{year}{month}{day}.{time}.gz"
        ext = ".gz"

    else:

        url = f"http://archive.routeviews.org/{probe}/bgpdata/{year}.{month}/RIBS/rib.{year}{month}{day}.{time}.bz2"
        ext = ".bz2"

    probe_dir = DATA_PATH / probe
    probe_dir.mkdir(parents=True, exist_ok=True)

    filename = url.split("/")[-1]

    local_path = probe_dir / filename

    check = subprocess.run(
        ["wget", "--spider", url],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if check.returncode != 0:

        print(f"Missing URL: {url}")
        return

    if not local_path.exists():

        subprocess.run(
            ["wget", url, "-O", str(local_path)],
            check=False
        )

    else:

        print(f"Exists: {local_path}")

    csv_path = probe_dir / f"{date}.csv"

    if not csv_path.exists():

        cmd = f"bgpdump -m {local_path} > {csv_path}"

        subprocess.run(cmd, shell=True)

    else:

        print(f"CSV exists: {csv_path}")

# =====================================================
# DELETE INTERMEDIATE FILES
# =====================================================

def delete_table(date):

    probes = PROBES

    year = date[:4]
    month = date[4:6]
    day = date[6:8]

    time = "0000"

    for probe in probes:

        ext = ".gz" if probe.startswith("rrc") else ".bz2"

        rib_name = (
            f"bview.{year}{month}{day}.{time}{ext}"
            if ext == ".gz"
            else f"rib.{year}{month}{day}.{time}{ext}"
        )

        rib_file = DATA_PATH / probe / rib_name
        csv_file = DATA_PATH / probe / f"{date}.csv"

        if rib_file.exists():
            rib_file.unlink()

        if csv_file.exists():
            csv_file.unlink()

# =====================================================
# COMBINE TABLES
# =====================================================

def combine_table(date):

    output_dir = DATA_PATH / "bgptables" / date

    output_dir.mkdir(parents=True, exist_ok=True)

    for probe in PROBES:

        csv_file = DATA_PATH / probe / f"{date}.csv"

        output_file = output_dir / f"{probe}.csv"

        try:

            first_chunk = True

            chunks = pd.read_csv(
                csv_file,
                sep="|",
                header=None,
                usecols=[2,3,7],
                names=["type","IP","IGP"],
                on_bad_lines="skip",
                chunksize=100000
            )

            for chunk in chunks:

                chunk = chunk[
                    (chunk["IGP"] == "IGP") &
                    (chunk["type"] == "B")
                ]

                chunk["Probe"] = probe

                chunk = chunk[
                    ["IP","Probe"]
                ].drop_duplicates()

                chunk.to_csv(
                    output_file,
                    mode="a",
                    header=first_chunk,
                    index=False
                )

                first_chunk = False

        except Exception as e:

            print(f"{probe}: {e}")

# =====================================================
# PIPELINE
# =====================================================

def download_ribs(date):

    targets = [
        [date, probe]
        for probe in PROBES
    ]

    with Pool(NUM_WORKERS) as p:

        p.map(
            download_one_probe,
            targets
        )

def get_bgp_table(date):

    download_ribs(date)

    combine_table(date)

    delete_table(date)
    
if __name__ == "__main__":

    get_bgp_table(DATE)