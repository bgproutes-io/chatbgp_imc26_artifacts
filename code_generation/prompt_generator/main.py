import os
import json
import tiktoken
import random
from os import listdir
from os.path import isfile, join
from pathlib import Path

REPRODUCIBILITY_SEED = 13

random.seed(REPRODUCIBILITY_SEED)

QUESTION_OUTPUT_HINT = {
    1: "final_answer: number of ASes",

    2: "final_answer: average AS path length",

    3: "final_answer: list of ASes",

    4: "final_answer: list of ASes",

    5: "final_answer: shortest distance",

    6: "final_answer: Yes or No",

    7: "final_answer: list of ASes",

    8: "final_answer: number of ASes",

    9: "final_answer: number of ASes",

    10: "final_answer: Unix timestamp",

    11: "final_answer: Unix timestamp",

    12: (
        "final_answer: list of dictionaries "
        "in the format "
        "{'vp': str(vantage_point.unique_id), "
        "'last_time': Unix timestamp}"
    ),

    13: (
    "final_answer: dictionary in the format "
    "{'status': 'connected' or 'disconnected', "
    "'date': 'YYYY-MM-DDTHH:MM:SS' or null}"
    ),

    14: "final_answer: Yes or No",

    15: "final_answer: Yes or No",

    16: (
        "final_answer: list of dictionaries "
        "in the format "
        "{'vp': str(vantage_point.unique_id), "
        "'updates': integer}"
    ),

    17: (
        "final_answer: list of dictionaries "
        "in the format "
        "{'vp': str(vantage_point.unique_id), "
        "'hour': 'YYYY-MM-DD %H:00:00',"
        "'count': integer}"
    ),

    18: "final_answer: list of updates",

    19: "final_answer: list of updates",

    20: (
        "final_answer: list of AS paths "
        "(space-separated strings)"
    ),

    21: "final_answer: list of updates",

    22: "final_answer: number of prefixes",

    23: "final_answer: list of updates",

    24: "final_answer: Yes or No",

    25: "final_answer: Yes or No",

    26: "final_answer: list of ASes",

    27: "final_answer: number of bogon prefixes",

    28: (
        "final_answer: list of AS paths "
        "(space-separated strings)"
    ),

    29: "final_answer: ratio between 0 and 1",

    30: "final_answer: number of prefixes",

    31: (
        "final_answer: dictionary mapping "
        "str(vantage_point.unique_id) "
        "to RIB sizes (integers)"
    ),

    32: "final_answer: number of distinct communities",

    33: "final_answer: list of ASes",

    34: "final_answer: proportion between 0 and 1",

    35: "final_answer: proportion between 0 and 1",

    36: (
        "final_answer: list of dictionaries "
        "in the format "
        "{'vp': str(vantage_point.unique_id), "
        "'increase_pct': percentage (0-100)}"
    ),

    37: "final_answer: list of prefixes",

    38: "final_answer: percentage between 0 and 100",

    39: "final_answer: list of communities",
}


# =====================================================
# LOAD QUESTIONS
# =====================================================

def get_questions(
    dir_question_spec,
    dir_question_infile,
    ignore_questions_list=[]
):

    question_dic = {}
    id_to_question = {}

    with open(dir_question_spec, 'r') as fd:
        data = json.load(fd)

    with open(dir_question_infile, 'r') as fd2:
        data2 = json.load(fd2)

    for question in data:

        if 'code_skeleton' not in data[question]:
            continue

        qid_tmp = int(
            data[question]['code_skeleton']
            .replace('question', '')
            .replace('.py', '')
        )

        if qid_tmp in ignore_questions_list:
            continue

        id_to_question[qid_tmp] = question

        if question in data2:
            question_dic[question] = list(data2[question].keys())
        else:
            question_dic[question] = []

    return id_to_question, question_dic


# =====================================================
# GENERATE PROMPT INPUT
# =====================================================

def generate_input(
    STOP_AFTER_ALL_QUESTION=True,
    PROMPT_MAX_TOKEN=None,
    ignore_questions_list=[],
    outfile='prompt.txt'
):

    dir_question_spec = '../../question_generator/questions.json'
    dir_question_infile = '../../question_generator/questions_all.json'
    dir_function_spec = './specs/'
    dir_code_snippet = '../code_skeleton/optimized_codes'

    id_to_question, question_list = get_questions(
        dir_question_spec,
        dir_question_infile,
        ignore_questions_list
    )

    question_list = list(question_list.keys())

    random.shuffle(question_list)

    enc = tiktoken.get_encoding("o200k_base")
    
    prompt_all = r"""
You are an expert Python software engineer specialized in BGP routing analysis.

Your ONLY task is:
convert BGP routing questions into FULL EXECUTABLE PYTHON CODE.
"""

    prompt_all += """

==================================================
TRAINING EXAMPLES START
==================================================
"""

    stop = False

    MAX_QUESTIONS = 39

    selected_questions = list(id_to_question.keys())

    random.shuffle(selected_questions)

    selected_questions = selected_questions[:MAX_QUESTIONS]

    idd = 1

    while True:

        for qid_tmp in selected_questions:

            main_question = id_to_question[qid_tmp]

            print('training:', main_question)

            messages, precise_question_selected = generate_prompt(
                main_question,
                dir_question_infile,
                dir_question_spec,
                dir_code_snippet,
            )

            if len(messages) == 0:
                continue

            prompt_tmp = ""

            prompt_tmp += f"\nUSER QUESTION{idd}:\n"
            prompt_tmp += messages[0]['content']

            prompt_tmp += "\nEXECUTABLE PYTHON CODE:\n"
            prompt_tmp += messages[1]['content']

            prompt_tmp += "\n"

            idd += 1

            if (
                PROMPT_MAX_TOKEN is not None and
                len(enc.encode(prompt_all + prompt_tmp)) > PROMPT_MAX_TOKEN
            ):
                stop = True
                break

            prompt_all += prompt_tmp

        if stop or STOP_AFTER_ALL_QUESTION:
            break

    prompt_all += generate_prompt_spec(dir_function_spec)

    prompt_all += r"""
==================================================
TRAINING EXAMPLES END
==================================================

DO NOT:
- explain
- summarize
- analyze
- discuss
- ask questions

DO:
- directly generate executable Python code

- ALWAYS extract QUESTION_ID and SET_ID exactly from evaluation question metadata
- ALWAYS define:

question_id = <QUESTION_ID>
set_id = <SET_ID>

- for regex and pattern matching, adhere to PostgreSQL regex syntax

ALWAYS define:

time
size
final_answer

ALWAYS save outputs as:

answer_file = (f"../../evaluation/eval_results/XoX/answer{question_id}.json")
"""

    with open(outfile, 'w') as fd:
        fd.write(prompt_all)

    print('> Number of tokens used:', len(enc.encode(prompt_all)))
    print('> Output stored in file:', outfile)

    return prompt_all


# =====================================================
# FUNCTION SPECS
# =====================================================

def generate_prompt_spec(dir_function_spec):

    prompt = ''

    for filename in [
        join(dir_function_spec, f)
        for f in listdir(dir_function_spec)
        if isfile(join(dir_function_spec, f))
    ]:

        with open(filename, 'r') as fd:
            s = fd.read()

        prompt += '\n\n\n' + s

    return prompt

# =====================================================
# GENERATE SINGLE PROMPT
# =====================================================

def generate_prompt(
    main_question,
    dir_question_infile,
    dir_question_spec,
    dir_code_snippet,
    outfile=None
):

    messages = []

    with open(dir_question_infile, 'r') as fd:
        data = json.load(fd)

    precise_question_list = list(data[main_question].keys())

    if len(precise_question_list) == 0:
        return [], ''

    random.shuffle(precise_question_list)

    precise_question_selected = precise_question_list.pop(0)

    user_message = {
        "role": "user",
        "content": precise_question_selected
    }

    assistant_message = {
        "role": "assistant",
        "content": generate_code_question(
            main_question,
            precise_question_selected,
            dir_question_infile,
            dir_question_spec,
            dir_code_snippet
        )
    }

    messages.append(user_message)
    messages.append(assistant_message)

    if outfile is not None:

        with open(outfile, 'w') as fd_out:
            fd_out.write(
                '\n'.join(
                    list(map(lambda x: str(x), messages))
                )
            )

    return messages, precise_question_selected


# =====================================================
# GENERATE CODE
# =====================================================

def generate_code_question(
    main_question,
    precise_question,
    dir_question_infile,
    dir_question_spec,
    dir_code_snippet
):

    with open(dir_question_spec, 'r') as fd:
        data = json.load(fd)

    main_question_params = data[main_question]['params']

    code_skeleton = dir_code_snippet + '/{}'.format(
        data[main_question]['code_skeleton']
    )

    with open(dir_question_infile, 'r') as fd:
        data = json.load(fd)

    precise_question_params = data[main_question][precise_question]

    params = {}

    for p in main_question_params:

        if p in precise_question_params:

            params[p] = precise_question_params[p]

            if p == 'vp':
                params[p] = params[p].split(',')

        else:
            params[p] = None

    with open(code_skeleton, 'r') as file:
        python_code = file.read()

    for p in params:

        if p == 'asxy' and params[p] is not None:

            python_code = python_code.replace(
                'param_{}'.format(p),
                str(params[p])
            )

            python_code = python_code.replace(
                'param_asx',
                str(params[p].split(',')[0])
            )

            python_code = python_code.replace(
                'param_asy',
                str(params[p].split(',')[1])
            )

        elif p == 'time_interval':

            if params[p] is not None:

                python_code = python_code.replace(
                    'param_time_interval_start',
                    '"' + str(
                        params[p].split(' - ')[0]
                    ).replace(' ', '-') + '"'
                )

                python_code = python_code.replace(
                    'param_time_interval_end',
                    '"' + str(
                        params[p].split(' - ')[1]
                    ).replace(' ', '-') + '"'
                )
        elif p == "ip_protocol":

            if str(params[p]) in ["4", "6"]:

                python_code = python_code.replace(
                "param_ip_protocol",
                str(params[p])
                )

            else:

                python_code = python_code.replace(
                "param_ip_protocol",
                "None"
                )

        elif p == 'community_set' and params[p] is not None:

            regexp = '&'.join([
                '(^| )' + c + '( |$)'
                for c in params[p].split(',')
            ])

            python_code = python_code.replace(
                'param_community_set',
                '"' + regexp + '"'
            )

        elif p == 'prefix' and params[p] is not None:

            python_code = python_code.replace(
                'param_prefix',
                '"' + params[p].replace('.', r'\.') + '"'
            )

        elif p == 'time' and params[p] is not None:

            python_code = python_code.replace(
                'param_{}'.format(p),
                '"' + str(params[p]).replace(' ', '-') + '"'
            )

        elif isinstance(params[p], str):

            python_code = python_code.replace(
                'param_{}'.format(p),
                '"' + str(params[p]) + '"'
            )

        else:

            python_code = python_code.replace(
                'param_{}'.format(p),
                str(params[p])
            )

    return python_code


# =====================================================
# CREATE N SETS OF 39 QUESTIONS
# =====================================================

def generate_question_sets(
    json_file,
    questions_file,
    n_sets=5,
    seed=None,
    output_dir=f"../../question_generator/eval_questions/"
):

    if seed is not None:
        random.seed(seed)

    os.makedirs(output_dir, exist_ok=True)

    with open(json_file, 'r') as f:
        data = json.load(f)

    with open(questions_file, 'r') as f:
        question_data = json.load(f)

    all_sets = {}

    for set_id in range(1, n_sets + 1):

        print(f"\n{'='*60}")
        print(f"Generating Set {set_id}")
        print(f"{'='*60}")

        result = {}
        result_gpt = []

        qid = 1

        for category in data:

            if category not in question_data:
                continue

            category_questions = data[category]

            if not category_questions:
                continue

            # Prefer questions WITH parameters
            with_params = [
                q for q, p in category_questions.items()
                if p
            ]

            pool = (
                with_params
                if with_params
                else list(category_questions.keys())
            )

            selected_question = random.choice(pool)

            result[category] = {
                "question": selected_question,
                "parameters": category_questions[selected_question]
            }

            hint = QUESTION_OUTPUT_HINT.get(
            qid,
            "the requested results"
            )

            question_text = (
            f"QUESTION_ID={qid}\n"
            f"SET_ID={set_id}\n\n"
            f"{selected_question}\n\n"
            f"The final answer in output must be {hint}."
            )

            result_gpt.append(question_text)

            print(f"Q{qid}: {selected_question}")

            qid += 1

        all_sets[f"set_{set_id}"] = result

        # Save detailed JSON
        detailed_path = os.path.join(
            output_dir,
            f"evaluation_set_{set_id}.json"
        )

        with open(detailed_path, 'w') as f:
            json.dump(result, f, indent=2)

        # Save GPT version
        gpt_path = os.path.join(
            output_dir,
            f"evaluation_set_{set_id}_gpt.json"
        )

        with open(gpt_path, 'w') as f:
            json.dump(result_gpt, f, indent=2)

        print(f"\n✅ Saved Set {set_id}")

    # Save all sets together
    all_sets_path = os.path.join(
        output_dir,
        "all_evaluation_sets.json"
    )

    with open(all_sets_path, 'w') as f:
        json.dump(all_sets, f, indent=2)

    print(f"\n✅ Saved all sets to: {all_sets_path}")

    return all_sets


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    # ================================================
    # GENERATE TRAINING PROMPT
    # ================================================

    generate_input(
        STOP_AFTER_ALL_QUESTION=True
    )

    # ================================================
    # GENERATE EVALUATION SETS
    # ================================================

    input_file = '../../question_generator/questions_all.json'

    questions_file = '../../question_generator/questions.json'

    generate_question_sets(
        json_file=input_file,
        questions_file=questions_file,
        n_sets=1,
        output_dir= Path("../../question_generator/eval_questions/")
    )
