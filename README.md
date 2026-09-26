# LegalFam evaluation package

Replication package for *A Citation-Grounded Multi-Agent LLM System for Trustworthy Family Law
Orientation in Peru* (Mori, Delgado and Rivadeneyra, Universidad Peruana de Ciencias Aplicadas).

It contains everything the paper refers to as "the released package": the deterministic scorer,
the question sets, the stored responses of the five ablation arms, the patcher that builds each
arm from the production workflow, the scope boundary set with its coding and probe, the
citation-resolver bench, the fault-injection experiment and the exported n8n workflows. The system
itself (frontend, backend, agentic flow, message broker) lives in the other repositories of the
[LegalFam](https://github.com/LegalFam) organization.

The ratings of the twelve legal experts are not included, to protect their anonymity.

## What needs model access

| Task | Gemini API | Other services |
|---|:-:|---|
| Re-scoring the stored run, all reports and figures | no | none |
| Citation-resolver bench | no | none |
| Checking that each arm is the patched production workflow | no | none |
| Fault-injection summaries from the stored records | no | none |
| Re-running the fault-injection experiment | no | backend, frontend, PostgreSQL, RabbitMQ (the agent is mocked) |
| Collecting new ablation or boundary-set responses | yes | n8n with the workflows in `n8n/`, a Gemini File Search store holding `work/corpus/`, the processing API from `agentic-flow` |
| Re-running the scope probe | yes | n8n with `n8n/scope-probe/` imported (only the Parser runs) |

Everything in the first four rows runs offline from a clean clone, each command in under a minute. New runs
call the model and will not reproduce the stored responses token for token: the reported figures
are computed from the stored responses.

## Requirements

- Python 3.10 or later (checked with 3.12.2) and the two packages in `requirements.txt`
  (`pydantic` 2.10.4, `pydantic-settings` 2.7.0). The scorer uses no other third-party package.
- For the fault-injection experiment only: Node.js 20 or later, JDK 21, Docker.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The commands that run inside `api/` read the corpus location from `CORPUS_DIR`:

```bash
export CORPUS_DIR=../work/corpus   # PowerShell: $env:CORPUS_DIR = "../work/corpus"
```

## Reproducing the paper

Run from the repository root unless the command starts with `cd api`.

| Command | Reproduces |
|---|---|
| `python scripts/check_reproducibility.py` | Re-scores the stored run three times under `PYTHONHASHSEED` 0, 1 and 2, checks that the three outputs are byte-identical to each other and to the committed ones, and prints the headline figures: traceability 85.7 %, 2.24 articles per response, article recall 69.7 %, 117/117 correctly located citations (Abstract; Section "What is measured, and how") |
| `cd api && python -m eval.score --run eval/runs/ablation && python -m eval.report --run eval/runs/ablation` | Regenerates `per_question.jsonl`, `results.json` and `report.md` in `api/eval/runs/ablation/`. `report.md` holds the ablation results table (per-arm means, main effects and interaction), the paired contrasts with McNemar/Wilcoxon tests and 95 % bootstrap intervals over 4,000 resamples, the control-arm table, citation quality (157 citations, 97.5 % verbatim, all located) and readability (Tables "Ablation results", "The control arm"; Sections "Citation quality", "The cost of each component") |
| `python scripts/extra_figures.py` | Figures the report does not print: Table "`full` against `base`, paired", Table "What each arm exposes to checking", Table "Latency per arm", the retry counts of the `full` arm (92 attempts, 18 transport and 11 application failures) and the three-pass scope probe (1 of 45 out-of-scope passes admitted, 30/30 in scope, 12/12 mixed with the out-of-scope part marked in 10; `gen-001` and `gen-002` rejected among the 63 evaluation questions) |
| `cd api && python -m eval.locator_bench --per-document 150` | Table "Locator resolution against ground truth": 4,495 positives (899 per mode × 5 modes), 4,437 correct (98.7 %), 0 partial, 0 wrong, 58 declined, 0 false accepts over 1,770 negatives. `--per-document 300` and `--seed 11` give the robustness checks in the same section |
| `cd api && python -m eval.scope report --run eval/runs/scope` | Table "The 30-question boundary set through the full system" from `scope_coding.csv` (15/15 out-of-scope refused, 0/10 in-scope refused, 4/4 mixed answered on their in-scope part only) |
| `python scripts/check_arms.py` | Section "Ablation design": rebuilds every arm by patching its production workflow and compares it with the arm that was run |
| `python fault-injection/analyze.py fault-injection/results/final` | Table "Delivery under injected faults" (S0–S7, 450 trials). `fault-injection/results/final-s8` gives S8 (50 trials) |
| `cd api && python -m eval.corpus_articles --verify-dataset eval/dataset/family_law_v1.jsonl` | Checks that every expected article in the question set exists in the corpus |

The scorer writes CRLF line endings and a backslashed run path on Windows; the committed outputs
are the POSIX ones. `check_reproducibility.py` normalises only those two differences before
comparing, and compares the three seeds with each other byte for byte.

## Contents

```
api/app/                      citation resolver and corpus index (verbatim from agentic-flow)
api/eval/                     scorer, report, bench, scope coding, ablation runner and patcher
api/eval/dataset/             family_law_v1.jsonl (63 questions), adversarial.jsonl (30), propositions.json
api/eval/runs/ablation/       stored responses per arm + per_question.jsonl, results.json, report.md
api/eval/runs/scope/          boundary-set responses, scope_coding.csv, scope_results.json, report.md
api/eval/runs/scope-probe/    probe_results.jsonl (307 classifier calls)
work/corpus/                  the 62 corpus documents, named as in Appendix D
n8n/workflows/                production workflows as described in the paper (with the scope rule)
n8n/workflows/eval/           the full arm used for the boundary set
n8n/ablation/                 the production workflows and the five arms that produced the stored run
n8n/scope-probe/              the two probes that run the Parser alone (ablation-time and current)
fault-injection/              mock agent, fault proxy, Playwright runner, analysis, per-trial records
scripts/                      reproducibility checks and the figures the report does not print
```

`api/eval/README.md` and `fault-injection/README.md` are the original working notes, in Spanish.
They document every metric in detail and the local environments used for the runs.

### Question sets

Each line of `family_law_v1.jsonl` has `id`, `category`, `question` (Spanish), `expected_articles`
(norm and article), `expected_norms`, `must_mention` (required legal terms), `must_not_mention`,
`expects_specialist_support` and `risk`. The questions were written by the authors.

Each line of `adversarial.jsonl` has `id`, `family`, `scope_label` (`FUERA` out of scope, `DENTRO`
in scope, `PARCIAL` mixed), `question` and `justification`, the reasoning behind the label.
`runs/scope/scope_coding.csv` codes every response as R1 substantive, R2 scope refusal,
R3 clarification request or R4 system error, with whether it cited articles and, for mixed items,
whether it covered the in-scope part and whether it developed the out-of-scope one.

### Stored responses

`runs/ablation/<arm>.jsonl` keeps every attempt, failed ones included, with the question, HTTP
status, error, latency and the full response returned by the workflow (answer, citations with
passage and locator, confidence, next steps). The scorer uses the first successful attempt per
question. Citations in `full.jsonl` carry the locators assigned by the current resolver, re-applied
to the passages and chunks the run retrieved. `runs/scope/full.jsonl` is used only for scope
classification; no figure is computed from its locators.

### Arms and workflows

`api/eval/ablation/arms.py` defines each arm as a list of patches over the production workflow.
Each patch is anchored to literal text and fails if the anchor is missing.
`python -m eval.ablation.build_workflows --source <production workflow> --out <dir>` writes the
arms. The four factorial arms were built from `n8n/ablation/production-6235c2b.json` and the
`no_xai_inline` control from `production-2eefb01.json` (the file names are the `agentic-flow`
commits). The only difference between the rebuilt and the stored factorial arms is the node id of
`Build Response Parser Failure`.

### Scope probe

`n8n/scope-probe/scope-probe-old.json` and `scope-probe-new.json` are the `full` workflow cut right
after the Parser Agent: its output goes straight to a `Respond Probe` node, so no retrieval or
answer generation runs. `old` carries the Parser used in the ablation run (identical to the one in
`n8n/ablation/production-6235c2b.json`) and `new` the current Parser with the scope rule
(identical to `n8n/workflows/LegalFam Message Flow.json`). Their webhooks are
`/webhook/scope-probe-old` and `/webhook/scope-probe-new`.

`scripts/run_probe.py` sends every question to both probes and appends one row per call to a JSONL
file. The stored `api/eval/runs/scope-probe/probe_results.jsonl` came from one pass over the 63
evaluation questions (`--rep 0 family_law_v1.jsonl`) and three passes over the boundary set
(`--rep 0`, `1` and `2` with `adversarial.jsonl`), 307 calls in total; a call that fails is kept
with `ok: false`, excluded from the counts and sent again on the next invocation. The boundary set
was renamed once after the run (ids from the working prefix `adv2-` to `adv-`, file from
`adversarial_v2.jsonl` to `adversarial.jsonl`), and rows from an earlier draft of the set were
dropped; no other change was made to the raw output.

### Fault injection

Scenarios, each run 50 times: S0 no fault; S1a connection reset for 30 s; S1b reset for 12 min;
S2 silent blackhole for 12 min; S3 acknowledgement requests aborted for 12 min; S4 tab closed and
reopened 15 min later; S5 message broker stopped for 12 min; S6 backend killed and restarted;
S7 agent failure during a 30 s outage; S8 backend killed while the agent call is in flight. The
definitions are in `fault-injection/runner/run.mjs` and the proxy modes in
`fault-injection/fault-proxy/proxy.mjs`. Records in `results/final/` were produced with frontend
`2cd0305` and backend `f5a0bc5`, and S8 in `results/final-s8/` with frontend `a730cda` and backend
`ec0fdd3`. The other folders under `results/` are the smoke test and the pilots, run before and
after fixing the six defects the experiment found; the "before" figures in the paper come from
`piloto/` (S2, 0 of 5 delivered) and `piloto-s8/` (S8, 0 of 4). The runner expects to sit inside a backend
checkout; to re-run it, use branch `fault-injection-experiment` of
[LegalFam/backend](https://github.com/LegalFam/backend), where the same harness lives under
`experiments/fault-injection/`, and follow `fault-injection/README.md`.

## Citation

See `CITATION.cff`.

## License

Code: MIT (`LICENSE`). Data: CC BY 4.0 (`LICENSE-DATA`). The corpus consists of official
Peruvian legal texts, which are not subject to copyright; see `LICENSE-DATA`.
