"""Collect evidence for grading: metrics snapshot, log validation, trace count."""
import json
import sys
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8000"
LOG_PATH = Path("data/logs.jsonl")


def main() -> None:
    print("=" * 60)
    print("EVIDENCE COLLECTION REPORT")
    print("=" * 60)

    # 1. Metrics snapshot (dashboard data)
    try:
        r = httpx.get(f"{BASE_URL}/metrics", timeout=10.0)
        metrics = r.json()
        print("\n--- Metrics (/metrics) ---")
        print(f"Traffic (total requests):  {metrics['traffic']}")
        print(f"Latency P50:               {metrics['latency_p50']:.1f} ms")
        print(f"Latency P95:               {metrics['latency_p95']:.1f} ms")
        print(f"Latency P99:               {metrics['latency_p99']:.1f} ms")
        print(f"Avg cost:                  ${metrics['avg_cost_usd']:.4f}")
        print(f"Total cost:                ${metrics['total_cost_usd']:.4f}")
        print(f"Tokens in (total):         {metrics['tokens_in_total']}")
        print(f"Tokens out (total):        {metrics['tokens_out_total']}")
        print(f"Error breakdown:           {metrics['error_breakdown']}")
        print(f"Quality avg:               {metrics['quality_avg']:.2f}")
        print(f"\n6 Dashboard panels ready: Latency | Traffic | Errors | Cost | Tokens | Quality")
    except Exception as e:
        print(f"\n[ERROR] Cannot reach /metrics: {e}")

    # 2. Health check (tracing status)
    try:
        r = httpx.get(f"{BASE_URL}/health", timeout=10.0)
        health = r.json()
        print(f"\n--- Health (/health) ---")
        print(f"App OK:                {health['ok']}")
        print(f"Tracing enabled:       {health['tracing_enabled']}")
        print(f"Active incidents:      {health['incidents']}")
    except Exception as e:
        print(f"\n[ERROR] Cannot reach /health: {e}")

    # 3. Log validation
    if LOG_PATH.exists():
        records = []
        for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        print(f"\n--- Logs (data/logs.jsonl) ---")
        print(f"Total log records:     {len(records)}")
        cids = set()
        pii_leaks = 0
        enriched = 0
        for rec in records:
            cid = rec.get("correlation_id", "")
            if cid and cid != "MISSING":
                cids.add(cid)
            raw = json.dumps(rec)
            if "@" in raw or "4111" in raw or "0987654321" in raw:
                pii_leaks += 1
            if all(k in rec for k in ("user_id_hash", "session_id", "feature", "model")):
                enriched += 1
        print(f"Unique correlation IDs: {len(cids)}")
        print(f"PII leaks detected:     {pii_leaks}")
        print(f"Enriched records:       {enriched}/{len(records)}")
    else:
        print("\n[WARN] data/logs.jsonl not found. Run the app and send requests first.")

    print("\n" + "=" * 60)
    print("Collect screenshots for grading-evidence.md")
    print("1. Langfuse trace list (>= 10 traces)")
    print("2. One full trace waterfall")
    print("3. JSON log with correlation_id")
    print("4. Log with PII redaction")
    print("5. Dashboard with 6 panels")
    print("6. Alert rules + runbook link")
    print("=" * 60)


if __name__ == "__main__":
    main()
