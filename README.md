# Artifacts for Submission #52 to IMC 2026

This repository contains the artifacts accompanying paper submission #52:

**"XoX: A System for Fast, Accurate, and Intuitive Querying of Large-Scale BGP Datasets"**

The source code is provided exclusively for review purposes. All software remains the intellectual property of the authors and is distributed under an **All Rights Reserved** license.

---

# Repository Structure

```text
question_generator/     Question generation pipeline
download_size/          Download-volume estimation scripts
code_generation/        Code skeletons and generation artifacts
prompt_generator/       Prompt construction and execution framework
bgpstream/              Prompt-engineered BGPStream implementations
evaluation/             Evaluation scripts and artifacts
```

---

# Important Notes

## ⚠️ Question Numbering

Question identifiers in this repository do **not** correspond to the numbering used in the submitted paper.

Repository numbering follows the ordering defined in:

```text
code_generation/questions/questions.json
```

For example:

> "What is the average length of an AS path in the routing table?"

corresponds to **Question 2**, whose corresponding code snippet is:

```text
question2.py
```

## ⚠️ Script Executability

Most scripts in this repository are **not directly executable**.

This is intentional and occurs for two primary reasons:

1. Some scripts depend on the proprietary `pyXoXapi` Python library, which is intentionally withheld to preserve anonymity during the review process.

2. Some scripts contain macros/placeholders that require instantiation with concrete parameter values before execution.

These artifacts are nevertheless included to:

* Allow reviewers to inspect implementation details and methodology
* Demonstrate generated code structure and logic
* Illustrate how the `pyXoXapi` interface is used
* Provide representative examples of generated code snippets

The only scripts that are directly executable without modifications are explicitly marked using the 🚀 emoji.

---

# Question Generator

Directory:

```text
question_generator/
```

## Files

### `questions.json`

Original set of 39 questions.

### `questions_template.json`

Templates used to generate additional question instances.

### `questions_all.json`

Expanded question set generated from the original 39 questions.

### `param_collector.py`

Queries `pyXoXapi` to extract parameter values for each date.

The downloaded data volume measured during this phase is also used as the baseline representing unoptimized `pyXoXapi`.

### `param_selector.py`

Selects appropriate parameters for each question category.

### `question_generator.py`

Generates question instances using templates and selected parameters.

---

# Download Size Analysis

Directory:

```text
download_size/
```

Scripts used to estimate downloaded data volumes.

## Files

### `map_vp_collector.py`

Maps VP IP addresses used in queries to collectors.

### `probes_list.py`

List of collectors.

### `bgpstream.py`

Download-size estimation using a BGPStream-based approach.

### `bgp2go.py`

Download-size estimation using a BGP2Go-style approach.

---

# Code Generation

Directory:

```text
code_generation/
```

## Code Skeletons

### `code_skeleton/optimized_codes/`

39 optimized Python code skeletons designed to minimize downloaded data volume.

### `code_skeleton/xox_codes/`

39 GPT-generated code skeletons corresponding to the original questions.

Macros/placeholders are automatically instantiated by:

```text
prompt_generator/code_runner.py
```

## Macro Definitions

| Macro                       | Description                       |
| --------------------------- | --------------------------------- |
| `param_ip_protocol`         | `ipv4`, `ipv6`, or both           |
| `param_vp`                  | List of vantage points            |
| `param_time`                | Timestamp (`MM/DD/YYYY-HH:MM:SS`) |
| `param_asx`                 | ASN                               |
| `param_asy`                 | ASN                               |
| `param_time_interval_start` | Start timestamp                   |
| `param_time_interval_end`   | End timestamp                     |
| `param_prefix`              | IP prefix                         |

---

# Prompt Generator

## 🚀 `prompt_generator/main.py`

Generates prompts for few-shot learning.

Using the provided inputs, this script automatically generates prompts for few-shot learning.

Additionally, it generates evaluation questions in two formats:

Prompt-ready format — intended to be queried to ChatGPT after prompting in order to obtain XoX-generated code snippets.
Parameterized format — contains macros/placeholders that are later instantiated with concrete values and executed using the optimized code skeletons.

Generated evaluation questions are stored in:

question_generator/eval_questions/

These generated artifacts are used throughout the evaluation pipeline for benchmarking and correctness analysis.

Usage
pip install -r requirements.txt
python3 main.py

Copy the generated prompt into ChatGPT-4o and issue a query such as:

> Rank the IPv6 vantage points based on the number of updates they collected on November 30, 2025.

Expected behavior: generation of a valid code snippet.

## `prompt_generator/code_runner.py`

Executes generated code from:

* `optimized_codes`
* `xox_codes`

---

# Prompt Engineering for BGPStream-Based Code Generation

Directory:

```text
bgpstream/
```

### `prompt.txt`

Prompt-engineering instructions (~25000 tokens).

### `codes/`

39 BGPStream implementations generated after prompt engineering.

---

# Evaluation and Results

Directory:

```text
evaluation/
```

## BGPStream Benchmark (Table 2)

Directory:

```text
evaluation/bgpstream/
```

Contains:

* 10 benchmark code skeletons
* Utility scripts
* Parallelized retrieval functions for updates and RIB dumps

## Figure 3

Contains:

* An original XoX-generated script
* Minor visualization modifications
* Reduced VP count (5 instead of 20) to decrease runtime

## Correctness Evaluation

### `correctness_evaluator.py`

Compares:

* `xox_codes`
* `optimized_codes`

using Jaccard similarity.
