"""Regenerate each ablation arm from the production workflow it was built from and compare.

Usage (from the repository root): python scripts/check_arms.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ABLATION = ROOT / "n8n" / "ablation"
SOURCES = {
    "production-6235c2b.json": ["full", "no_rag", "no_xai", "base"],
    "production-2eefb01.json": ["no_xai_inline"],
}


def without_node_ids(workflow: dict) -> dict:
    return {**workflow, "nodes": [{k: v for k, v in node.items() if k != "id"} for node in workflow["nodes"]]}


def main() -> int:
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        for source, arms in SOURCES.items():
            command = [sys.executable, "-m", "eval.ablation.build_workflows",
                       "--source", str(ABLATION / source), "--out", tmp]
            for arm in arms:
                command += ["--arm", arm]
            subprocess.run(command, cwd=ROOT / "api", check=True, stdout=subprocess.DEVNULL,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
            for arm in arms:
                name = f"legalfam-eval-{arm}.json"
                built = json.loads((Path(tmp) / name).read_text(encoding="utf-8"))
                stored = json.loads((ABLATION / name).read_text(encoding="utf-8"))
                same = without_node_ids(built) == without_node_ids(stored)
                ids = sum(a["id"] != b["id"] for a, b in zip(built["nodes"], stored["nodes"]))
                ok &= same
                print(f"{arm:15} from {source}: identical apart from node ids={same}, differing node ids={ids}")
    print("OK" if ok else "MISMATCH")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
