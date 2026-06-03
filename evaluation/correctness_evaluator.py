import json
import numpy as np
from pathlib import Path

DATA_DIR = Path("./eval_results/")

METHOD_1 = "OP"
METHOD_2 = "XoX"

# =====================================================
# LOAD RESULTS
# =====================================================

def load_result(method, qid):

    file = DATA_DIR / method / f"answer{qid}.json"

    if not file.exists():
        return None

    with open(file) as f:
        return json.load(f)

# =====================================================
# NORMALIZATION FOR FLOAT/INTEGER 
# =====================================================

def normalize(value):

    if isinstance(value, (int, float)):

        value = float(value)

        if abs(value - round(value)) < 1e-3:
            return str(round(value))

        return str(round(value, 3))

    return str(value)

# =====================================================
# FINAL ANSWER -> SET
# =====================================================

def final_answer_to_set(answer):

    value = answer.get("final_answer")

    if value is None:
        return set()

    if isinstance(value, (list, set)):

        return {normalize(v) for v in value}

    return {normalize(value)}

# =====================================================
# JACCARD
# =====================================================

def jaccard_similarity(a, b):

    if not a and not b:
        return 1.0

    return len(a & b) / len(a | b)

# =====================================================
# FIND AVAILABLE QUESTIONS
# =====================================================

question_ids = sorted([
    int(f.stem.replace("answer", ""))
    for f in (DATA_DIR / METHOD_1).glob("answer*.json")
])

# =====================================================
# EVALUATION
# =====================================================

similarities = []

perfect = 0
high = 0
medium = 0
incorrect = 0
not_answered = 0

for qid in question_ids:

    result1 = load_result(METHOD_1, qid)
    result2 = load_result(METHOD_2, qid)

    if result1 is None or result2 is None:
        continue

    set1 = final_answer_to_set(result1)
    set2 = final_answer_to_set(result2)

    # empty answer
    if len(set2) == 0:

        sim = 0
        not_answered += 1
        category = "Not answered"

    else:

        sim = jaccard_similarity(set1, set2)

        if sim == 1.0:

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

    similarities.append(sim)

    print(f"Q{qid}: {sim:.3f} ({category})")

total = len(similarities)

print("\n-------------------------------------------")
print("Outcome\t\t\tJaccard\t\tRuns (%)")
print("-------------------------------------------")

print(f"Perfect match\t\t= 1.0\t\t{100*perfect/total:.2f}")
print(f"High similarity\t\t>= 0.8\t\t{100*high/total:.2f}")
print(f"Medium similarity\t>= 0.5\t\t{100*medium/total:.2f}")
print(f"Incorrect\t\t< 0.5\t\t{100*incorrect/total:.2f}")
print(f"Not answered\t\t-\t\t{100*not_answered/total:.2f}")