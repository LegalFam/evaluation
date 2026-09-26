"""Figures reported in the paper that the scorer's report.md does not print.

Usage (from the repository root): python scripts/extra_figures.py
"""
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

EVAL = Path(__file__).resolve().parent.parent / "api" / "eval"
ABLATION = EVAL / "runs" / "ablation"
sys.path.insert(0, str(EVAL.parent))
from eval import report  # noqa: E402


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def latency_table() -> None:
    print("Latency per arm, seconds (Table 'Latency per arm'; inclusive percentiles)")
    print(f"{'arm':15}{'median':>8}{'p90':>8}{'p95':>8}{'max':>8}")
    rows = read_jsonl(ABLATION / "per_question.jsonl")
    for arm in ["base", "no_rag", "no_xai", "full", "no_xai_inline"]:
        latencies = sorted(r["latency_ms"] / 1000 for r in rows if r["arm"] == arm and r["ok"])
        cuts = statistics.quantiles(latencies, n=20, method="inclusive")
        print(f"{arm:15}{statistics.median(latencies):8.1f}{cuts[17]:8.1f}{cuts[18]:8.1f}{latencies[-1]:8.1f}")


def attempts() -> None:
    print("\nAttempts per arm (Section 'What is measured, and how')")
    for arm in ["full", "no_rag", "no_xai", "base", "no_xai_inline"]:
        rows = read_jsonl(ABLATION / f"{arm}.jsonl")
        failed = [r for r in rows if not r["ok"]]
        transport = sum(r["status"] is None for r in failed)
        worst, tries = Counter(r["id"] for r in rows).most_common(1)[0]
        print(f"  {arm:15} {len(rows)} attempts, {transport} transport failures, "
              f"{len(failed) - transport} application failures, most attempts: {worst} ({tries})")


def scope_probe() -> None:
    print("\nScope probe, current Parser, three passes per question (Section 'Scope classification')")
    labels = {r["id"]: r["scope_label"] for r in read_jsonl(EVAL / "dataset" / "adversarial.jsonl")}
    probe = [r for r in read_jsonl(EVAL / "runs" / "scope-probe" / "probe_results.jsonl") if r["probe"] == "new"]
    boundary = [r for r in probe if r["dataset"] == "adversarial.jsonl" and r["ok"]]
    for label in ["FUERA", "DENTRO", "PARCIAL"]:
        passes = [r for r in boundary if labels[r["id"]] == label]
        admitted = [r for r in passes if r["category"] != "error"]
        line = f"  {label:8} admitted {len(admitted)} of {len(passes)} passes"
        if label == "PARCIAL":
            line += f", out-of-scope part marked in {sum(bool(r['out_of_scope_parts']) for r in admitted)}"
        print(line)
    evaluation = [r for r in probe if r["dataset"] == "family_law_v1.jsonl"]
    rejected = sorted(r["id"] for r in evaluation if r["category"] == "error")
    print(f"  63 evaluation questions: rejects {', '.join(rejected)}, admits {len(evaluation) - len(rejected)}")


def full_vs_base() -> None:
    print("\nfull against base, paired (Table 'full against base'; difference, 95% bootstrap CI, p)")
    rows = report.load_rows(ABLATION)
    for metric in ["articles_surfaced", "article_recall", "traceable", "must_mention_coverage", "correct"]:
        result = report.contrast(report.pivot(rows, metric), metric, "full", "base")
        low, high = result["ci95"]
        extra = f", discordant {result['wins']} vs {result['losses']}" if result["test"] == "McNemar" else ""
        print(f"  {metric:22} {result['difference']:+.3f} [{low:.3f}, {high:.3f}] "
              f"{result['test']} n={result['n']} p={result['p']:.2g}{extra}")


def exposed_totals() -> None:
    print("\nWhat each arm exposes to checking, run totals (Table 'What each arm exposes')")
    print(f"{'arm':15}{'assertions':>11}{'mentions':>9}{'distinct':>9}{'citations':>10}{'checkable':>10}{'fabricated':>11}")
    rows = [r for r in report.load_rows(ABLATION) if r["ok"]]
    for arm in ["full", "no_xai", "no_xai_inline", "no_rag", "base"]:
        own = [r for r in rows if r["arm"] == arm]
        mentions = sum(r["mentions_total"] for r in own)
        distinct = sum(r["articles_from_text"] for r in own)
        citations = sum(r["citations"] for r in own)
        print(f"{arm:15}{sum(r['normative_claims'] for r in own):11}{mentions:9}{distinct:9}{citations:10}"
              f"{mentions + citations:10}{sum(r['hallucinated_explicit'] for r in own):11}")
    print("  mentions = every article mention in the prose; distinct = distinct articles named in the prose")


if __name__ == "__main__":
    full_vs_base()
    exposed_totals()
    latency_table()
    attempts()
    scope_probe()
