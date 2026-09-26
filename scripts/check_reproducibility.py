"""Re-score the stored ablation run under three hash seeds and compare with the committed outputs.

Usage (from the repository root): python scripts/check_reproducibility.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "api"
RUN = Path("eval") / "runs" / "ablation"
OUTPUTS = ["per_question.jsonl", "results.json", "report.md"]
SEEDS = ["0", "1", "2"]


def normalize(data: bytes) -> bytes:
    # Windows writes CRLF and backslashes in the run path; the committed files are the POSIX output.
    return data.replace(b"\r\n", b"\n").replace(b"eval\\\\runs\\\\", b"eval/runs/")


def score(seed: str) -> dict[str, bytes]:
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(API / RUN, Path(tmp) / RUN)
        env = {
            **os.environ,
            "PYTHONHASHSEED": seed,
            "PYTHONPATH": str(API),
            "CORPUS_DIR": str(ROOT / "work" / "corpus"),
            "PYTHONIOENCODING": "utf-8",
        }
        env.pop("GEMINI_API_KEY", None)
        for module in ("eval.score", "eval.report"):
            subprocess.run(
                [sys.executable, "-m", module, "--run", str(RUN)],
                cwd=tmp, env=env, check=True, stdout=subprocess.DEVNULL,
            )
        return {name: (Path(tmp) / RUN / name).read_bytes() for name in OUTPUTS}


def headline(per_question: bytes) -> None:
    rows = [json.loads(line) for line in per_question.decode("utf-8").splitlines()]
    full = [r for r in rows if r["arm"] == "full"]
    n = len(full)
    locatable = sum(r["locator_correct"] + r["locator_partial"] + r["locator_wrong"] for r in full)
    print(f"full arm, {n} questions")
    print(f"  traceability         {sum(r['traceable'] for r in full) / n:.1%}")
    print(f"  articles per answer  {sum(r['articles_surfaced'] for r in full) / n:.2f}")
    print(f"  article recall       {sum(r['article_recall'] for r in full if r['expected_articles']) / sum(1 for r in full if r['expected_articles']):.1%}")
    print(f"  correct locators     {sum(r['locator_correct'] for r in full)}/{locatable}")


def main() -> int:
    runs = {seed: score(seed) for seed in SEEDS}
    ok = True
    for name in OUTPUTS:
        digests = {seed: hashlib.sha256(runs[seed][name]).hexdigest()[:16] for seed in SEEDS}
        same_across_seeds = len(set(digests.values())) == 1
        committed = normalize((API / RUN / name).read_bytes())
        same_as_committed = normalize(runs[SEEDS[0]][name]) == committed
        ok &= same_across_seeds and same_as_committed
        print(f"{name:20} seeds {' '.join(digests.values())}  "
              f"identical={same_across_seeds}  matches committed={same_as_committed}")
    headline(runs[SEEDS[0]]["per_question.jsonl"])
    print("OK" if ok else "MISMATCH")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
