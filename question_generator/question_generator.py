import json
import random
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict,Any
from param_selector import QUESTION_FUNCTIONS

# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 13
random.seed(RANDOM_SEED)

VP_COUNT = 10
SAMPLES_PER_QUESTION = 10

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_FILE = BASE_DIR / "questions_all_template.json"

OUTPUT_FILE = BASE_DIR / "questions_all.json"

logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s")

# ============================================================
# TIME RANDOMIZATION
# ============================================================

def ordinal(n: int) -> str:

    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {
            1: "st",
            2: "nd",
            3: "rd"
        }.get(n % 10, "th")

    return f"{n}{suffix}"


def format_datetime_variants(dt: datetime) -> Dict[str, str]:

    day = ordinal(dt.day)

    long_date = dt.strftime(f"%B {day}, %Y")

    short_date = dt.strftime("%m/%d/%Y")

    shorter_date = (f"{dt.month}/"f"{dt.day}/"f"{str(dt.year)[2:]}")

    time_12h = dt.strftime("%I:%M %p").lstrip("0")

    time_full = dt.strftime("%I:%M:%S %p").lstrip("0")

    return {
        "long_date": long_date,
        "short_date": short_date,
        "shorter_date": shorter_date,
        "time_12h": time_12h,
        "time_full": time_full,
    }

def randomize_time_text(time_input: str) -> str:

    if " - " in time_input:

        start_str, end_str = (time_input.split(" - "))
        
        start_dt = datetime.strptime(start_str.strip(),"%Y-%m-%dT%H:%M:%S")

        end_dt = datetime.strptime(end_str.strip(),"%Y-%m-%dT%H:%M:%S")
        
        s = format_datetime_variants(start_dt)

        e = format_datetime_variants(end_dt)

        templates = [
            
            f"during the period from {s['long_date']} to {e['long_date']}",

            f"over the interval between {s['long_date']} and {e['long_date']}",

            f"between {s['long_date']} and {e['long_date']}",

            f"from {s['shorter_date']} to {e['shorter_date']}",
        ]

        return random.choice(
            templates
        )

    dt = datetime.strptime(time_input,"%Y-%m-%dT%H:%M:%S")

    t = format_datetime_variants(dt)

    templates = [
        
        f"on {t['long_date']}",

        f"during {t['long_date']}",

        f"on {t['short_date']}",

        f"on {t['shorter_date']}",

        f"at {t['time_full']} on {t['long_date']}",

        f"throughout {t['long_date']}",
    ]

    return random.choice(
        templates
    )

# ============================================================
# PARAMETER HANDLING
# ============================================================

def format_parameter(param_name: str,value: Any) -> str:

    if param_name in ["time","time_interval"]:
        return randomize_time_text(value)

    elif param_name == "vp":

        vps = [x.strip() for x in value.split(",")]

        return random.choice([

            "BGP peers " + ", ".join(vps),

            "VP IPs " + ", ".join(vps),

            "VPs " + ", ".join(vps),

            "collectors " + ", ".join(vps),

            "routers " + ", ".join(vps),

            "vantage points " + ", ".join(vps),
        ])

    elif param_name == "asxy":

        if isinstance(value, list):
            a, b = value

        elif "," in value:
            a, b = value.split(",")

        else:
            return str(value)

        return random.choice([

            f"AS{a} and AS{b}",

            f"Autonomous Systems {a} and {b}",

            f"AS pairs {a} and {b}",
        ])

    elif param_name == "ip_protocol":

        if str(value) == "4":
            return "IPv4"

        elif str(value) == "6":
            return "IPv6"

        return ""

    return str(value)

# ============================================================
# QUESTION GENERATOR
# ============================================================

def generate_questions(question_templates, dataset):

    generated = {}

    for question_id, (category, groups) in enumerate(
        question_templates.items(),
        start=1
    ):

        generated[category] = {}

        for group in groups:

            required = group["parameters"]

            templates = group["templates"]

            valid_rows = []

            for row in dataset:

                # ONLY use rows from SAME question generator
                if row.get("question_id") != question_id:
                    continue

                missing = [p for p in required if p not in row]

                if not missing:
                    valid_rows.append(row)

            for row in valid_rows:

                replacements = {
                    p: format_parameter(p, row[p])
                    for p in required
                }

                for template in templates:

                    question = template.format(**replacements)

                    generated[category][question] = {
                        p: row[p]
                        for p in required
                    }

    return generated

# ============================================================
# DATASET CREATION
# ============================================================

def build_dataset(samples_per_question=20,vp_count_range=(VP_COUNT,VP_COUNT)):

    dataset = []

    for qid, func in (QUESTION_FUNCTIONS.items()):

        for _ in range(samples_per_question):
            try:
                n = random.randint(*vp_count_range)
                row = func(n)
                row["question_id"] = qid
                dataset.append(row)

            except Exception as e:

                logging.warning(f"Question {qid} "f"failed: {e}")
                
    return dataset
# ============================================================
# MAIN
# ============================================================
def main():

    with open(TEMPLATE_FILE,"r") as f:

        templates = json.load(f)

    dataset = build_dataset(samples_per_question = SAMPLES_PER_QUESTION)

    generated = (generate_questions(templates,dataset))

    filtered = {}

    for cat, questions in (generated.items()):
        
        valid = {}
        
        for q, params in (questions.items()):
            
            vp = params.get("vp","")
            
            if (isinstance(vp, str) and not vp.strip()):
                continue

            valid[q] = params

        if valid:

            filtered[cat] = valid

    final_output = filtered

    with open(OUTPUT_FILE,"w") as f:

        json.dump(final_output,f,indent=2,ensure_ascii=False)

if __name__ == "__main__":

    main()