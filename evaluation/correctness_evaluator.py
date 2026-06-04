import json
from pathlib import Path

DATA_DIR = Path("./eval_results/")

METHOD_1 = "OP"
METHOD_2 = "XoX"

# ==========================================
# QUESTION TYPES
# ==========================================

YESNO_QUESTIONS = {6, 14, 15, 24, 25}

INTEGER_QUESTIONS = {
    1, 5, 8, 9, 22, 27, 30, 32
}

FLOAT_QUESTIONS = {
    2, 29, 34, 35, 38
}

TIME_QUESTIONS = {
    10, 11
}

LIST_QUESTIONS = {
    3, 4, 7,
    18, 19, 20, 21, 23,
    26, 28,
    33,
    37,
    39
}

DICT_QUESTIONS = {
    12, 13, 16, 17, 31, 36
}

# ==========================================
# LOAD
# ==========================================

def load_result(method, qid):

    file = DATA_DIR / method / f"answer{qid}.json"

    if not file.exists():
        return None

    with open(file) as f:
        return json.load(f)

# ==========================================
# JACCARD
# ==========================================

def jaccard_similarity(a, b):

    if not a and not b:
        return 1.0

    return len(a & b) / len(a | b)

# ==========================================
# SIMILARITY
# ==========================================

def compute_similarity(qid, r1, r2):

    v1 = r1.get("final_answer")
    v2 = r2.get("final_answer")

    if v1 is None and v2 is None:
        return 1.0

    if v1 is None or v2 is None:
        return 0.0

    try:

        # YES / NO
        if qid in YESNO_QUESTIONS:

            return float(
                str(v1).lower().strip()
                ==
                str(v2).lower().strip()
            )

        # INTEGER
        if qid in INTEGER_QUESTIONS:

            a = int(v1)
            b = int(v2)

            if a == b:
                return 1.0

            return max(
                0,
                1 - abs(a - b) / max(abs(a), abs(b), 1)
            )

        # FLOAT
        if qid in FLOAT_QUESTIONS:

            a = float(v1)
            b = float(v2)

            return max(
                0,
                1 - abs(a - b) / max(abs(a), abs(b), 1e-3)
            )

        # TIME
        if qid in TIME_QUESTIONS:

            diff = abs(float(v1) - float(v2))

            if diff <= 1000:
                return 1.0
            elif diff <= 3600:
                return 0.9
            elif diff <= 21600:
                return 0.8
            elif diff <= 86400:
                return 0.5

            return 0.0

        # LISTS
        if qid in LIST_QUESTIONS:

            s1 = set(
                map(
                    str,
                    v1 if isinstance(v1, list) else [v1]
                )
            )

            s2 = set(
                map(
                    str,
                    v2 if isinstance(v2, list) else [v2]
                )
            )

            return jaccard_similarity(
                s1,
                s2
            )

        # DICTS
        if qid in DICT_QUESTIONS:

            try:

                # convert each dictionary into canonical string
                s1 = set(
                    json.dumps(
                        x,
                        sort_keys=True
                    )
                    for x in (
                        v1 if isinstance(v1, list)
                        else [v1]
                    )
                )

                s2 = set(
                    json.dumps(
                        x,
                        sort_keys=True
                    )
                    for x in (
                        v2 if isinstance(v2, list)
                        else [v2]
                    )
                )

                return jaccard_similarity(
                    s1,
                    s2
                )

            except:

                return 0.0
            
    except:

        return 0.0

# ==========================================
# QUESTION IDS
# ==========================================

question_ids = sorted({

    int(f.stem.replace("answer", ""))

    for method in [METHOD_1, METHOD_2]

    for f in (DATA_DIR / method).glob(
        "answer*.json"
    )
})

# ==========================================
# EVALUATION
# ==========================================

perfect = 0
high = 0
medium = 0
incorrect = 0
not_answered = 0

total = 0

for qid in question_ids:

    r1 = load_result(METHOD_1, qid)
    r2 = load_result(METHOD_2, qid)

    if r1 is None or r2 is None:

        not_answered += 1

        print(
            f"Q{qid}: 0.000 (Not answered)"
        )

        total += 1

        continue

    sim = compute_similarity(
        qid,
        r1,
        r2
    )

    if sim == 1:

        perfect += 1
        category = "Perfect match"

    elif sim >= 0.8:

        high += 1
        category = "High similarity"

    elif sim >= 0.5:

        medium += 1
        category = "Medium similarity"

    else:

        incorrect += 1
        category = "Incorrect"

    print(
        f"Q{qid}: {sim:.3f} ({category})"
    )

    total += 1

# ==========================================
# SUMMARY
# ==========================================

print("\n--------------------------------")
print("Outcome\t\t\tRuns (%)")
print("--------------------------------")

print(
    f"Perfect match\t\t{100*perfect/total:.2f}"
)

print(
    f"High similarity\t\t{100*high/total:.2f}"
)

print(
    f"Medium similarity\t{100*medium/total:.2f}"
)

print(
    f"Incorrect\t\t{100*incorrect/total:.2f}"
)

print(
    f"Not answered\t\t{100*not_answered/total:.2f}"
)