"""Send each question to the two scope probes (old and new Parser) and append the Parser output.

Needs n8n running with n8n/scope-probe/*.json imported and active, and Gemini credentials.
Usage (from the repository root):
    python scripts/run_probe.py <out.jsonl> --rep 0 family_law_v1.jsonl adversarial.jsonl
    python scripts/run_probe.py <out.jsonl> --rep 1 adversarial.jsonl
    python scripts/run_probe.py <out.jsonl> --rep 2 adversarial.jsonl
"""
import argparse
import json
import sys
from pathlib import Path

API = Path(__file__).resolve().parent.parent / "api"
sys.path.insert(0, str(API))
from eval.run_ablation import call_webhook, load_dataset  # noqa: E402

DATASETS = API / "eval" / "dataset"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("datasets", nargs="+")
    parser.add_argument("--rep", type=int, default=0)
    parser.add_argument("--base-url", default="http://localhost:5678")
    args = parser.parse_args()

    done = set()
    if args.out.exists():
        rows = map(json.loads, args.out.read_text(encoding="utf-8").splitlines())
        done = {(r["probe"], r["id"], r["rep"]) for r in rows if r["ok"]}

    with args.out.open("a", encoding="utf-8") as handle:
        for name in args.datasets:
            for item in load_dataset(DATASETS / name):
                for probe in ("old", "new"):
                    if (probe, item["id"], args.rep) in done:
                        continue
                    result = call_webhook(f"{args.base_url}/webhook/scope-probe-{probe}", None,
                                          "X-N8N-Token", item["question"], 120)
                    output = (result.get("response") or {}).get("output") or {}
                    row = {"probe": probe, "rep": args.rep, "dataset": name, "id": item["id"],
                           "ok": result["ok"] and bool(output), "category": output.get("category"),
                           "out_of_scope_parts": output.get("out_of_scope_parts"),
                           "information_sufficiency": output.get("information_sufficiency"),
                           "error": result.get("error")}
                    handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                    handle.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
