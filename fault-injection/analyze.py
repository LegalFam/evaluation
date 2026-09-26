"""Resume results.jsonl del runner en summary.md, por escenario.

Uso: py analyze.py results/final
"""

import json
import math
import statistics
import sys
from collections import Counter, OrderedDict
from pathlib import Path

SCENARIO_ORDER = ["S0", "S1a", "S1b", "S2", "S3", "S4", "S5", "S6", "S7"]
Z = 1.959963984540054


def wilson(successes, n):
    if n == 0:
        return (float("nan"), float("nan"))
    p = successes / n
    denominator = 1 + Z**2 / n
    centre = (p + Z**2 / (2 * n)) / denominator
    half = Z * math.sqrt(p * (1 - p) / n + Z**2 / (4 * n**2)) / denominator
    return (max(0.0, centre - half), min(1.0, centre + half))


def nearest_rank(values, q):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(q * len(ordered)) - 1)]


def delivery_seconds(trial):
    if trial["scenario"] == "S5":
        reference = trial["t_fault_start"]
    else:
        reference = trial.get("t_fault_end") or trial.get("t0")
    return (max(trial["t_visible"], trial.get("t_read") or 0) - reference) / 1000


def pct(value):
    return f"{value * 100:.1f} %"


def load(results_dir):
    trials = [json.loads(line) for line in (results_dir / "results.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    grouped = OrderedDict((s, []) for s in SCENARIO_ORDER)
    for trial in trials:
        grouped.setdefault(trial["scenario"], []).append(trial)
    return trials, OrderedDict((s, t) for s, t in grouped.items() if t)


def summarize(results_dir):
    trials, grouped = load(results_dir)
    commits = sorted({(t["commit_frontend"], t["commit_backend"]) for t in trials})
    lines = [f"# Resumen — `{results_dir.name}`", ""]
    lines.append("Commits: " + "; ".join(f"frontend `{f}`, backend `{b}`" for f, b in commits))
    lines.append("")

    lines.append("## Entrega")
    lines.append("")
    lines.append("| Escenario | n | Entregadas | % | IC 95 % (Wilson) | Mediana (s) | p90 (s) | Errores del runner |")
    lines.append("|---|--:|--:|--:|---|--:|--:|--:|")
    for scenario, items in grouped.items():
        n = len(items)
        delivered = [t for t in items if t.get("delivered")]
        low, high = wilson(len(delivered), n)
        times = [delivery_seconds(t) for t in delivered]
        median = f"{statistics.median(times):.1f}" if times else "—"
        p90 = f"{nearest_rank(times, 0.9):.1f}" if times else "—"
        errors = sum(1 for t in items if t.get("error"))
        lines.append(f"| {scenario} | {n} | {len(delivered)} | {pct(len(delivered) / n)} | [{pct(low)}; {pct(high)}] | {median} | {p90} | {errors} |")
    lines.append("")
    lines.append("Tiempo hasta la entrega = max(visible en pantalla, `READ`) − vuelta de la conexión (en S0, − t₀; en S4, − apertura de la página nueva; en S5, − caída de Rabbit, porque la respuesta llega por historial antes de que vuelva).")
    lines.append("")

    lines.append("## Camino de entrega")
    lines.append("")
    paths = ["sse", "history", "retry_sse", None]
    lines.append("| Escenario | sse | history | retry_sse | sin llegada |")
    lines.append("|---|--:|--:|--:|--:|")
    for scenario, items in grouped.items():
        counts = Counter(t.get("path") for t in items)
        lines.append(f"| {scenario} | " + " | ".join(str(counts.get(p, 0)) for p in paths) + " |")
    lines.append("")

    lines.append("## Duplicados, cobros y bloqueo")
    lines.append("")
    lines.append("| Escenario | Dup. transporte (pruebas / eventos extra) | Dup. pantalla | Dup. BD | Cobros dobles | Violaciones de bloqueo | Control de bloqueo |")
    lines.append("|---|---|--:|--:|--:|--:|---|")
    for scenario, items in grouped.items():
        transport = [t for t in items if t.get("sse_events_same_id", 0) > 1]
        extra_events = sum(t["sse_events_same_id"] - 1 for t in transport)
        dom = sum(1 for t in items if t.get("dom_copies", 0) > 1)
        database = sum(1 for t in items if t.get("db_assistant_rows", 0) > 1)
        double_charge = sum(
            1 for t in items
            if t.get("credit_transactions", 0) > 1 or t.get("subscription_delta", 0) > t.get("credits_charged", 0)
        )
        violations = sum(1 for t in items if t.get("lock_violation"))
        lock_checks = Counter(t.get("lock_check") for t in items)
        lock_text = ", ".join(f"{k}: {v}" for k, v in sorted(lock_checks.items(), key=lambda kv: str(kv[0])))
        lines.append(f"| {scenario} | {len(transport)} / {extra_events} | {dom} | {database} | {double_charge} | {violations} | {lock_text} |")
    lines.append("")
    lines.append("`subscription_delta` incluye el cobro de una consulta de control aceptada después de `READ`; en ese caso se revisa `notes`.")
    lines.append("")

    lines.append("## Estado final del outbox")
    lines.append("")
    lines.append("| Escenario | READ | PUBLISHED | PENDING | sin evento | attempt_count (mín–máx) |")
    lines.append("|---|--:|--:|--:|--:|---|")
    for scenario, items in grouped.items():
        statuses = Counter((t.get("outbox_final") or {}).get("status") for t in items)
        attempts = [t["outbox_final"]["attempt_count"] for t in items if t.get("outbox_final")]
        attempt_range = f"{min(attempts)}–{max(attempts)}" if attempts else "—"
        lines.append(f"| {scenario} | {statuses.get('READ', 0)} | {statuses.get('PUBLISHED', 0)} | {statuses.get('PENDING', 0)} | {statuses.get(None, 0)} | {attempt_range} |")
    lines.append("")

    batches = OrderedDict()
    for trial in trials:
        if trial.get("batch_id"):
            batches.setdefault((trial["scenario"], trial.get("t_fault_start")), []).append(trial)
    if batches:
        lines.append("## Tandas (S5, S6)")
        lines.append("")
        lines.append("| Tanda | Pruebas | Entregadas | Inicio del fallo | Fin del fallo |")
        lines.append("|---|--:|--:|---|---|")
        for items in batches.values():
            ids = sorted(t["trial_id"] for t in items)
            batch_id = f"{ids[0]} … {ids[-1]}"
            start = items[0].get("t_fault_start")
            end = items[0].get("t_fault_end")
            duration = f"{(end - start) / 1000:.1f} s" if start and end else "—"
            lines.append(f"| {batch_id} | {len(items)} | {sum(1 for t in items if t.get('delivered'))} | {start} | {end} ({duration}) |")
        lines.append("")

    failures = [t for t in trials if not t.get("delivered")]
    if failures:
        lines.append("## Pruebas no entregadas")
        lines.append("")
        for t in failures:
            outbox = t.get("outbox_final") or {}
            lines.append(
                f"- `{t['trial_id']}`: error={t.get('error')!r}, outbox={outbox.get('status')} "
                f"(intentos {outbox.get('attempt_count')}), visible={bool(t.get('t_visible'))}, read={bool(t.get('t_read'))}"
            )
        lines.append("")

    output = results_dir / "summary.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    summarize(Path(sys.argv[1]))
