import json
import subprocess
import os
import argparse
import time
import sys

TMP_DIR = "/tmp"

CODE_TYPES = {
    "optimized": "../code_skeleton/optimized_codes",
    "gpt": "../code_skeleton/xox_codes"
}

def inject_parameters(code, params, set_number, code_type):
    code = code.replace("SET_NUMBER_PLACEHOLDER", str(set_number))

    if code_type != "gpt":
        for key, value in params.items():

            if key == "asxy":
                asx, asy = value.split(",")
                code = code.replace("param_asx", asx.strip())
                code = code.replace("param_asy", asy.strip())

            elif key == "vp":
                vp_list = [v.strip() for v in value.split(",") if v.strip()]
                code = code.replace("param_vp", str(vp_list))

            elif key == "time":
                code = code.replace("param_time", f'"{value}"')

            elif key == "time_interval":
                start, end = value.split(" - ")
                code = code.replace(
                    "param_time_interval_start",
                    f'"{start.strip().replace(" ", "-")}"'
                )
                code = code.replace(
                    "param_time_interval_end",
                    f'"{end.strip().replace(" ", "-")}"'
                )

            elif key == "ip_protocol":
                if value in ["4", "6"]:
                    code = code.replace("param_ip_protocol", value)
                else:
                    code = code.replace("param_ip_protocol", "None")

            elif key == "asx":
                code = code.replace("param_asx", value)

            elif key == "asy":
                code = code.replace("param_asy", value)

            elif key == "prefix":
                code = code.replace("param_prefix", f'"{value}"')

            elif key == "community_set":
                code = code.replace("param_community_set", f'"{value}"')

        defaults = {
            "param_ip_protocol": "None"
        }

        for placeholder, replacement in defaults.items():
            code = code.replace(placeholder, replacement)

    return code

def execute_script(tmp_file, q_number):
    attempt = 1

    while True:
        try:
            result = subprocess.run(
                ["python3", tmp_file],
                check=True,
                capture_output=True,
                text=True
            )

            print(result.stdout)

            if result.stderr:
                print(result.stderr)

            print(f"✅ Q{q_number} finished successfully")
            break

        except subprocess.CalledProcessError as e:

            stdout = e.stdout.lower() if e.stdout else ""
            stderr = e.stderr.lower() if e.stderr else ""
            combined_output = stdout + stderr

            if (
                "rate limit" in combined_output
                or "429" in combined_output
                or "too many requests" in combined_output
                or "502 bad gateway" in combined_output
                or "invalid json response" in combined_output
                or "jsondecodeerror" in combined_output
            ):

                print(f"⏳ Rate limit detected for Q{q_number}")
                print(f"⏳ {combined_output}")
                print(f"⏳ Attempt #{attempt}")

                attempt += 1
                time.sleep(1200)
                continue

            print(f"❌ Q{q_number} crashed")
            print(f"Return code: {e.returncode}")

            if e.stdout:
                print("STDOUT:")
                print(e.stdout)

            if e.stderr:
                print("STDERR:")
                print(e.stderr)

            print("➡️ Moving to next question...")
            break

        except Exception as e:
            print(f"❌ Unexpected error in Q{q_number}: {e}")
            print("➡️ Moving to next question...")
            break

def main():

    parser = argparse.ArgumentParser(
        description="Artifact evaluation runner"
    )

    parser.add_argument(
        "--set",
        type=int,
        required=True,
        help="Evaluation set number"
    )

    args = parser.parse_args()
    set_number = args.set
    
    EVALUATION_FILE = (
        f"../../question_generator/eval_questions/evaluation_set_{set_number}.json"
    )
    
    print(f"SET={set_number}")
    print(f"Python={sys.version.split()[0]}")

    if not os.path.exists(EVALUATION_FILE):
        raise FileNotFoundError(
            f"Missing evaluation file: {EVALUATION_FILE}"
        )

    with open(EVALUATION_FILE, "r") as f:
        data = json.load(f)

    questions = list(data.keys())

    print(f"Questions={len(questions)}")

    os.makedirs(TMP_DIR, exist_ok=True)

    for code_type, code_dir in CODE_TYPES.items():

        print(f"\n{'='*60}")
        print(f"RUNNING: {code_type} | SET {set_number}")
        print(f"{'='*60}")

        for i, q in enumerate(questions, start=1):

            print(f"\n=== Running Q{i}: {data[q].get('question')} ===")

            params = data[q].get("parameters", {})

            script_path = os.path.join(
                code_dir,
                f"question{i}.py"
            )

            if not os.path.exists(script_path):
                print(f"❌ Missing script: {script_path}")
                continue

            with open(script_path, "r") as f:
                code = f.read()

            code = inject_parameters(
                code,
                params,
                set_number,
                code_type
            )

            tmp_file = os.path.join(
                TMP_DIR,
                f"{code_type}_set{set_number}_q{i}.py"
            )

            with open(tmp_file, "w") as f:
                f.write(code)

            print(f"TMP FILE: {tmp_file}")

            execute_script(
                tmp_file,
                i
            )

"""
for filename in os.listdir(TMP_DIR):

    if filename.startswith(
        ("optimized_set", "gpt_set")
    ) and filename.endswith(".py"):

        file_path = os.path.join(
            TMP_DIR,
            filename
        )

        try:
            os.remove(file_path)
            print(f"Removed: {file_path}")

        except Exception as e:
            print(f"Failed removing {file_path}: {e}")
"""

if __name__ == "__main__":
    main()